from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    WalletDetailSerializer,
    TransactionSerializer,
)
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from requests.exceptions import RequestException
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Wallet, Transaction,UserProfile
from django.urls import reverse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from pyotp import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
import base64
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .serializers import PaymentSerializer
from datetime import date
import uuid
import secrets
import stripe
from rest_framework.permissions import AllowAny, IsAuthenticated
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

def logoutuser(request):
    logout(request)
    return redirect(reverse('signin'))

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Check if a user with the same email already exists
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            # Generate a TOTP key for the user
            totp_key = self.generate_totp_key()
            # Create a new user with the User model
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=email,
                password=serializer.validated_data['password'],
                is_active=False,  # User starts as inactive
            )
            user.save()

            # Create a UserProfile for the new user
            user_profile = UserProfile(
                user=user,
                firstname=serializer.validated_data['firstname'],
                lastname=serializer.validated_data['lastname'],
                phone_number=serializer.validated_data['phone_number'],
                totp_key=totp_key
                # You can handle profile picture separately, depending on your requirements
            )
            user_profile.save()

            print(f'account created for {user}')
            # Generate a verification token for the user
            verification_token = default_token_generator.make_token(user)
            # Encode the user's ID
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            # Send the TOTP key to the user via email (for one-time use)
            self.send_verification_email(user, totp_key, request)
            # Check if a Wallet already exists for the user
            wallet, created = Wallet.objects.get_or_create(user=user)
            print(f"created wallet {wallet}")
            if created:
                # Wallet was created
                pass

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'message': 'Please check your email for verification instructions.', 'access_token': access_token, "uidb64": uidb64, "verification_token": verification_token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def generate_totp_key(self):
        # Generate a random secret key as bytes
        secret_key_bytes = secrets.token_bytes(20)  # 20 bytes (160 bits)
        # Convert the bytes to a base32-encoded string
        secret_key = base64.b32encode(secret_key_bytes).decode('utf-8')
        # Create a TOTP instance
        totp = TOTP(secret_key, interval=30)  # Replace 'your-secret-key' with your secret key
        # Generate the TOTP token
        totp_key = totp.now()
        print(totp_key)
        return totp_key

    def send_verification_email(self, user, totp_key, email):
            email_template = "verification_email.html"
            # API endpoint to send the email
            url = f"https://100085.pythonanywhere.com/api/email/"
            name = user.username
            EMAIL_FROM_WEBSITE = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Samanta Content Evaluator</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 2; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {name}, thank you for registering to our platform. Enter the OTP below to verify your email.</p>
                                <p style="font-size: 1.1em; text-align: center;">Your OTP for verification is: {totp}</p>
                                <p style="font-size: 1.1em; text-align: center;">If you did not create an account with us, you can ignore this email.</p>
                            </div>
                        </body>
                        </html>
                    """
            context = {
                "name":name,
                "totp":totp_key
            }

            email_content = EMAIL_FROM_WEBSITE.format(name=name, totp=totp_key, email=email)
            payload = {
                "toname": name,
                "toemail": user.email,
                "subject": "OTP Verification",
                "email_content": email_content,
            }
            response = requests.post(url, json=payload)
            print(totp_key)
            print(response.text)
            return response.text


@method_decorator(csrf_exempt, name='dispatch')
class OTPVerificationView(APIView):
    def post(self, request):
        totp_key = request.data.get('otp_key')
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            totp_key_from_profile = user.userprofile.totp_key
            if totp_key_from_profile == totp_key:
                # Activate the user
                user.is_active = True
                user.save()
                return Response({'message': 'Account verified and activated.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class SendMoney(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        sender = request.user
        sender_email = sender.email  # Access sender's email
        recipient_username = request.data.get("recipient_username")
        amount = request.data.get("amount")
        try:
            recipient = User.objects.get(username=recipient_username)
            recipient_email = recipient.email  # Access recipient's email
        except User.DoesNotExist:
            return Response({"message": "Recipient not found"}, status=status.HTTP_400_BAD_REQUEST)
        if sender == recipient:
            return Response({"message": "You cannot send money to yourself"}, status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({"message": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        sender_wallet = sender.wallet
        if sender_wallet.balance < amount:
            return Response({"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
        sender_wallet.balance -= amount
        sender_wallet.save()
        recipient_wallet = recipient.wallet
        recipient_wallet.balance += amount
        recipient_wallet.save()
        transaction = Transaction(wallet=sender.wallet, transaction_type="Transfer", amount=amount, status="Completed")
        transaction.save()
        transaction_time = transaction.timestamp
        #send sender the email
        self.sender_transaction_email(amount,sender,recipient_username,sender_email,transaction_time)
        self.recepient_transaction_email(amount,sender,recipient_username,recipient_email,transaction_time)
        return Response({"message": "Money sent successfully"}, status=status.HTTP_200_OK)
    
    def sender_transaction_email(self,amount,sender,recipient_username,sender_email,transaction_time):
            # API endpoint to send the email
            url = f"https://100085.pythonanywhere.com/api/email/"
            sender_name = sender.username
            EMAIL_FROM_WEBSITE = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE-edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Your Wallet Transaction Confirmation</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {sender_name},</p>
                                <p style="font-size: 1.1em; text-align: center;">You have successfully sent ${amount} to {recipient_username}.</p>
                                <p style="font-size: 1.1em; text-align: center;">Transaction time: {transaction_time}</p>
                                <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
                            </div>
                        </body>
                        </html>
                        """

            email_content = EMAIL_FROM_WEBSITE.format(sender_name=sender_name, amount=amount,recipient_username=recipient_username,transaction_time=transaction_time)
            payload = {
                "toname": sender_name,
                "toemail": sender_email,
                "subject": f"Transfer Money to {recipient_username}",
                "email_content": email_content,
            }
            response = requests.post(url, json=payload)
            print(response.text)
            return response.text
    
    def recepient_transaction_email(self,amount,sender,recipient_username,recipient_email,transaction_time):
            # API endpoint to send the email
            url = f"https://100085.pythonanywhere.com/api/email/"
            sender_name = sender.username
            EMAIL_FROM_WEBSITE = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE-edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Your Wallet Transaction Confirmation</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {recipient_username},</p>
                                <p style="font-size: 1.1em; text-align: center;">You have received ${amount} from {sender_name}.</p>
                                <p style="font-size: 1.1em; text-align: center;">Transaction time: {transaction_time}</p>
                                <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
                            </div>
                        </body>
                        </html>


                        """

            email_content = EMAIL_FROM_WEBSITE.format(sender_name=sender_name, amount=amount,recipient_username=recipient_username,transaction_time=transaction_time)
            payload = {
                "toname": sender_name,
                "toemail": recipient_email,
                "subject": f"Received Money from {sender_name}",
                "email_content": email_content,
            }
            response = requests.post(url, json=payload)
            print(response.text)
            return response.text

class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request)
        wallet = Wallet.objects.get(user=request.user)
        transactions = Transaction.objects.filter(wallet=wallet)
        wallet_serializer = WalletDetailSerializer(wallet)
        transactions_serializer = TransactionSerializer(transactions, many=True)

        data = {
            "wallet": wallet_serializer.data,
            "transactions": transactions_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)


class StripePayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("user", request.user)
            data = request.data
            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                amount = validate_data["amount"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            today = date.today()
            unique_id = uuid.uuid4()
            payment_id = str(unique_id)

            user_wallet = Wallet.objects.get(user=request.user)

            stripe_key = os.getenv("STRIPE_KEY", None)
            stripe.api_key = stripe_key

            session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "wallet topup",
                            },
                            "unit_amount": f"{(amount) * 100}",
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{'http://127.0.0.1:8000/api/wallet/v1/stripe-callback'}?payment_id={payment_id}",
                cancel_url=f"{'http://127.0.0.1:8000/api/wallet/v1/stripe-callback'}?payment_id={payment_id}",
                billing_address_collection="required",
                payment_intent_data={
                    "metadata": {
                        "description": "wallet topup",
                        "payment_id": payment_id,
                        "date": today,
                    }
                },
            )
            # print(session)
            transaction = Transaction(
                wallet=user_wallet,
                transaction_type="Deposit",
                status="Failed",
                amount=amount,
                session_id=session.id,
                payment_id=payment_id,
            )
            transaction.save()
            return Response(
                {"success": True, "approval_url": f"{session.url}"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Stripe verify Payment classs
class StripePaymentCallback(APIView):
    def get(self, request):
        try:
            payment_id = request.GET.get("payment_id")
            transaction = Transaction.objects.get(payment_id=payment_id)

            stripe_key = os.getenv("STRIPE_KEY", None)
            stripe.api_key = stripe_key

            payment_session = stripe.checkout.Session.retrieve(transaction.session_id)
            # print(payment_session)
            payment_status = payment_session["payment_status"]
            state = payment_session["status"]

            # Check the payment status
            if payment_status == "paid" and state == "complete":
                amount = payment_session["amount_total"] / 100
                # Access the associated wallet
                wallet = transaction.wallet

                if transaction.status == "Failed":
                    wallet.balance += Decimal(amount)
                    wallet.save()
                transaction.status = "sucessful"
                transaction.save()
                # Get the user's email address and name
                user_email = transaction.wallet.user.email
                user_name = transaction.wallet.user.username
                self.send_transaction_email(user_name, user_email, amount)

            # redirect to frontend url page
            redirect_url = f"https://100088.pythonanywhere.com/api/success"
            response = HttpResponseRedirect(redirect_url)
            return response
        except Exception as e:
            print("error", e)
            redirect_url = f"https://100088.pythonanywhere.com/api/success"
            response = HttpResponseRedirect(redirect_url)
            return response
        
    def send_transaction_email(self,user_name,user_email,amount):
            # API endpoint to send the email
            url = f"https://100085.pythonanywhere.com/api/email/"
            name = user_name
            EMAIL_FROM_WEBSITE = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Samanta Content Evaluator</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {name},</p>
                                <p style="font-size: 1.1em; text-align: center;">Your deposit was successful.</p>
                                <p style="font-size: 1.1em; text-align: center;">You have added an amount of ${amount} to your wallet.</p>
                                <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
                            </div>
                        </body>
                        </html>
                        """

            email_content = EMAIL_FROM_WEBSITE.format(name=name, amount=amount)
            payload = {
                "toname": name,
                "toemail": user_email,
                "subject": "Walllet Deposit",
                "email_content": email_content,
            }
            response = requests.post(url, json=payload)
            print(response.text)
            return response.text
