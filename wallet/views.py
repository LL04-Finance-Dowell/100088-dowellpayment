from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import (
    UserRegistrationSerializer,
    PaymentAuthorizationSerializer,
    WalletDetailSerializer,
    TransactionSerializer,
    ExternalPaymentSerializer,
    UserProfileSerializer,
    DowellPaymentSerializer,
)
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from requests.exceptions import RequestException
import requests
import random
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import (
    Wallet,
    Transaction,
    UserProfile,
    MoneyRequest,
    PaymentInitialazation,
)
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
from django.utils import timezone
import stripe
from rest_framework.permissions import AllowAny, IsAuthenticated
from decimal import Decimal
import os
from django.db.models import Q
from .supported_currency import stripe_supported_currency
import uuid
import json
import requests
from dotenv import load_dotenv

load_dotenv()


"""GET PAYPAL MODE DOWELL INTERNAL TEAM"""
dowell_paypal_mode = os.getenv("DOWELL_PAYPAL_LIVE_MODE")
if dowell_paypal_mode == "True":
    dowell_paypal_url = "https://api-m.paypal.com"
else:
    dowell_paypal_url = "https://api-m.sandbox.paypal.com"

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If the user with the given email exists, we can proceed to authentication.
        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            # Authentication successful
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({"success": True, "access_token": access_token})
        else:
            return Response(
                {"success": False, "error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.session.flush()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "Not logged in"}, status=status.HTTP_401_UNAUTHORIZED
        )


class PasswordResetRequestView(APIView):
    def post(self, request):
        data = request.data
        email = data["email"]
        print(email)
        try:
            user = User.objects.get(email=email)
            # Generate a TOTP key for the user
            totp_key = self.generate_totp_key()
            # Save the TOTP key to the user's profile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.totp_key = totp_key
            user_profile.save()
            # Send the TOTP key to the user via email or other communication method
            self.send_password_reset_email(user, totp_key)

            return Response({"message": "TOTP key sent to your email"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def send_password_reset_email(self, user, totp_key):
        # API endpoint to send the email
        url = f"https://100085.pythonanywhere.com/api/email/"
        name = user.username
        EMAIL_FROM_WEBSITE = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Samanta Content Evaluator</title>
                </head>
                <body>
                    <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 2; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                        <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                        <p style="font-size: 1.1em; text-align: center;">Dear {name}, you have requested a password reset.</p>
                        <p style="font-size: 1.1em; text-align: center;">To reset your password, click the link below:</p>
                        <p style="font-size: 1.1em; text-align: center;">Your OTP is: {totp_key}</p>
                        <p style="font-size: 1.1em; text-align: center;">If you did not request this password reset, you can ignore this email.</p>
                        
                    </div>
                </body>
                </html>
            """
        email_content = EMAIL_FROM_WEBSITE.format(name=name, totp_key=totp_key)
        payload = {
            "toname": name,
            "toemail": user.email,
            "subject": "Password Reset",
            "email_content": email_content,
        }
        response = requests.post(url, json=payload)
        return response.text

    def generate_totp_key(self):
        # Generate a random secret key as bytes
        secret_key_bytes = secrets.token_bytes(20)  # 20 bytes (160 bits)
        # Convert the bytes to a base32-encoded string
        secret_key = base64.b32encode(secret_key_bytes).decode("utf-8")
        # Create a TOTP instance
        totp = TOTP(
            secret_key, interval=30
        )  # Replace 'your-secret-key' with your secret key
        # Generate the TOTP token
        totp_key = totp.now()
        print(totp_key)
        return totp_key


class ResetPasswordOtpVerify(APIView):
    def post(self, request):
        data = request.data
        email = data["email"]
        otp = data["otp"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        stored_otp_key = user_profile.totp_key
        if otp == stored_otp_key:
            new_password = data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password reset successful"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )

        """AFTER THIS THE USER SHOULD BE REDIRECTED TO THE RESET PASSWORD TO ENTER A NEW PASSWORD"""


class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            # Generate a TOTP key for the user
            totp_key = self.generate_totp_key()
            # Save the TOTP key to the user's profile
            user_profile.totp_key = totp_key
            user_profile.save()
            # Send the TOTP key to the user via email or other communication method
            self.send_otp_email(user, totp_key)

            return Response(
                {"message": "OTP sent to your email"}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def send_otp_email(self, user, totp_key):
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
                                <p style="font-size: 1.1em; text-align: center;">Dear {name},</p>
                                <p style="font-size: 1.1em; text-align: center;">Your OTP for verification is: {totp}</p>
                                <p style="font-size: 1.1em; text-align: center;">If you did not request an OTP with us, you can ignore this email.</p>
                            </div>
                        </body>
                        </html>
                    """

        email_content = EMAIL_FROM_WEBSITE.format(name=name, totp=totp_key)
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

    def generate_totp_key(self):
        # Generate a random secret key as bytes
        secret_key_bytes = secrets.token_bytes(20)  # 20 bytes (160 bits)
        # Convert the bytes to a base32-encoded string
        secret_key = base64.b32encode(secret_key_bytes).decode("utf-8")
        # Create a TOTP instance
        totp = TOTP(
            secret_key, interval=30
        )  # Replace 'your-secret-key' with your secret key
        # Generate the TOTP token
        totp_key = totp.now()
        return totp_key


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = request.data.get("phone_number")
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")

            # Check if a user with the same email already exists
            email = serializer.validated_data["email"]
            username = email
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "Email already in use."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Generate a TOTP key for the user
            totp_key = self.generate_totp_key()
            # Create a new user with the User model
            user = User.objects.create_user(
                email=email,
                username=username,
                password=serializer.validated_data["password"],
                is_active=False,  # User starts as inactive
            )
            user.save()

            # Create a UserProfile for the new user
            user_profile = UserProfile(
                user=user,
                totp_key=totp_key,
                firstname=first_name,
                lastname=last_name,
                phone_number=phone_number
                # You can handle profile picture separately, depending on your requirements
            )
            user_profile.save()

            print(f"account created for {user}")
            self.send_verification_email(user, totp_key, request)
            # Check if a Wallet already exists for the user
            # Check if a Wallet already exists for the user
            wallet, created = Wallet.objects.get_or_create(user=user)

            # Update the wallet password if provided
            wallet_password = request.data.get("wallet_password")
            if wallet_password:
                wallet.password = make_password(str(wallet_password))
                wallet.save()
            print(f"created wallet {wallet}")
            if created:
                # Wallet was created
                pass

            return Response(
                {
                    "success": True,
                    "message": "Please check your email for verification instructions.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def generate_totp_key(self):
        # Generate a random secret key as bytes
        secret_key_bytes = secrets.token_bytes(20)  # 20 bytes (160 bits)
        # Convert the bytes to a base32-encoded string
        secret_key = base64.b32encode(secret_key_bytes).decode("utf-8")
        # Calculate the expiration time (30 minutes from now)
        expiration_time = timezone.now() + timezone.timedelta(minutes=30)
        # Create a TOTP instance
        totp = TOTP(
            secret_key, interval=30
        )  # Replace 'your-secret-key' with your secret key
        # Generate the TOTP token
        totp_key = totp.now()
        print(totp_key)
        return totp_key

    def send_verification_email(self, user, totp_key, email):
        # API endpoint to send the email
        url = f"https://100085.pythonanywhere.com/api/email/"
        name = user.username
        expiration_time = timezone.now() + timezone.timedelta(
            minutes=30
        )  # 30 minutes from now
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
                                <p style="font-size: 1.1em; text-align: center;">This OTP is valid until {expiration_time}.</p>
                                <p style="font-size: 1.1em; text-align: center;">If you did not create an account with us, you can ignore this email.</p>
                            </div>
                        </body>
                        </html>
                    """
        context = {"name": name, "totp": totp_key}

        email_content = EMAIL_FROM_WEBSITE.format(
            name=name, expiration_time=expiration_time, totp=totp_key, email=email
        )
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


@method_decorator(csrf_exempt, name="dispatch")
class OTPVerificationView(APIView):
    def post(self, request):
        totp_key = request.data.get("otp_key")
        email = request.data.get("email")

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
                return Response(
                    {"message": "Account verified and activated."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


# @method_decorator(csrf_exempt, name="dispatch")
# class SendMoney(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Get the user who is sending money (sender)
#         sender = request.user
#         sender_email = sender.email  # Access sender's email
#         # Get the wallet password from the request data
#         wallet_password = request.data.get("wallet_password")

#         # Verify the wallet password
#         if not check_password(str(wallet_password), sender.wallet.password):
#             return Response(
#                 {"message": "Incorrect wallet password"},
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )

#         # Get the recipient's account_no and amount from the request data
#         account_no = request.data.get("account_no")
#         amount = request.data.get("amount")

#         try:
#             # Try to find the wallet associated with the provided account_no
#             wallet = Wallet.objects.get(account_no=account_no)

# # Check if the wallet is associated with a user
# recipient = (
#     wallet.user
# )  # Assuming 'user' is the related name in your Wallet model
# print(recipient)
# recipient_email = recipient.email  # Access recipient's email
# recipient_username = recipient.username

#         except Wallet.DoesNotExist:
#             # If the wallet doesn't exist, return an error response
#             return Response(
#                 {"message": "Recipient's wallet not found"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         except User.DoesNotExist:
#             # If recipient doesn't exist, return an error response
#             return Response(
#                 {"message": "Recipient not found"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Check if the sender is trying to send money to themselves
#         if sender == recipient:
#             return Response(
#                 {"message": "You cannot send money to yourself"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Check if the amount is valid
#         if amount <= 0:
#             return Response(
#                 {"message": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         # Update the sender's wallet balance
#         sender_wallet = sender.wallet
#         if sender_wallet.balance < amount:
#             return Response(
#                 {"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST
#             )
#         sender_wallet.balance -= amount
#         sender_wallet.save()

#         # Update the recipient's wallet balance
#         recipient_wallet = recipient.wallet
#         recipient_wallet.balance += amount
#         recipient_wallet.save()

#         # Create a transaction record for the sender
#         transaction = Transaction(
#             wallet=sender.wallet,
#             transaction_type="Transfer",
#             amount=amount,
#             status="Completed",
#         )
#         transaction.save()
#         transaction_time = transaction.timestamp

#         # Create a transaction record for the recipient
#         recipient_transaction = Transaction(
#             wallet=recipient.wallet,
#             transaction_type="Received",
#             amount=amount,
#             status="Completed",
#         )
#         recipient_transaction.save()

#         # Send transaction confirmation emails to the sender and recipient
#         self.sender_transaction_email(
#             amount, sender, recipient_username, sender_email, transaction_time
#         )
#         self.recipient_transaction_email(
#             amount, sender, recipient_username, recipient_email, transaction_time
#         )

# # Return a success response
# return Response(
#     {"message": "Money sent successfully"}, status=status.HTTP_200_OK
# )

#     def sender_transaction_email(
#         self, amount, sender, recipient_username, sender_email, transaction_time
#     ):
#         # API endpoint to send the email
#         url = f"https://100085.pythonanywhere.com/api/email/"
#         sender_name = sender.username
#         EMAIL_FROM_WEBSITE = """
#                     <!DOCTYPE html>
#                         <html lang="en">
#                         <head>
#                             <meta charset="UTF-8">
#                             <meta http-equiv="X-UA-Compatible" content="IE-edge">
#                             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                             <title>Your Wallet Transaction Confirmation</title>
#                         </head>
#                         <body>
#                             <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
#                                 <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
#                                 <p style="font-size: 1.1em; text-align: center;">Dear {sender_name},</p>
#                                 <p style="font-size: 1.1em; text-align: center;">You have successfully sent ${amount} to {recipient_username}.</p>
#                                 <p style="font-size: 1.1em; text-align: center;">Transaction time: {transaction_time}</p>
#                                 <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
#                             </div>
#                         </body>
#                         </html>
#                         """

#         email_content = EMAIL_FROM_WEBSITE.format(
#             sender_name=sender_name,
#             amount=amount,
#             recipient_username=recipient_username,
#             transaction_time=transaction_time,
#         )
#         payload = {
#             "toname": sender_name,
#             "toemail": sender_email,
#             "subject": f"Transfer Money to {recipient_username}",
#             "email_content": email_content,
#         }
#         response = requests.post(url, json=payload)
#         print(response.text)
#         return response.text

#     def recipient_transaction_email(
#         self, amount, sender, recipient_username, recipient_email, transaction_time
#     ):
#         # API endpoint to send the email
#         url = f"https://100085.pythonanywhere.com/api/email/"
#         sender_name = sender.username
#         EMAIL_FROM_WEBSITE = """
#                     <!DOCTYPE html>
#                         <html lang="en">
#                         <head>
#                             <meta charset="UTF-8">
#                             <meta http-equiv="X-UA-Compatible" content="IE-edge">
#                             <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                             <title>Your Wallet Transaction Confirmation</title>
#                         </head>
#                         <body>
#                             <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
#                                 <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
#                                 <p style="font-size: 1.1em; text-align: center;">Dear {recipient_username},</p>
#                                 <p style="font-size: 1.1em; text-align: center;">You have received ${amount} from {sender_name}.</p>
#                                 <p style="font-size: 1.1em; text-align: center;">Transaction time: {transaction_time}</p>
#                                 <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
#                             </div>
#                         </body>
#                         </html>


#                         """

#         email_content = EMAIL_FROM_WEBSITE.format(
#             sender_name=sender_name,
#             amount=amount,
#             recipient_username=recipient_username,
#             transaction_time=transaction_time,
#         )
#         payload = {
#             "toname": sender_name,
#             "toemail": recipient_email,
#             "subject": f"Received Money from {sender_name}",
#             "email_content": email_content,
#         }
#         response = requests.post(url, json=payload)
#         print(response.text)
#         return response.text


class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        transactions = Transaction.objects.filter(wallet=wallet).order_by("-timestamp")
        wallet_serializer = WalletDetailSerializer(wallet)
        transactions_serializer = TransactionSerializer(transactions, many=True)

        user_data = {
            "id": request.user.id,
            "username": request.user.username,
            # Add any other user-related fields you want to include
        }

        data = {
            "user": user_data,  # Include user data in the response
            "wallet": wallet_serializer.data,
            "transactions": transactions_serializer.data,
        }

        return Response(data, status=status.HTTP_200_OK)

class PaypalPayment(APIView):
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
            url = f"{dowell_paypal_url}/v2/checkout/orders"
            client_id = os.getenv("PAYPAL_CLIENT_ID", None)
            client_secret = os.getenv("PAYPAL_SECRET_KEY", None)
            encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {encoded_auth.decode()}",
                "Prefer": "return=representation",
            }
            body = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{amount}",
                        }
                    }
                ],
                "payment_source": {
                    "paypal": {
                        "experience_context": {
                            "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                            "payment_method_selected": "PAYPAL",
                            "locale": "en-US",
                            "landing_page": "LOGIN",
                            "user_action": "PAY_NOW",
                            "return_url": f"{'http://127.0.0.1:8000/api/wallet/v1/paypal-callback'}",
                            "cancel_url": f"{'http://127.0.0.1:8000/api/wallet/v1/paypal-callback'}",
                        }
                    }
                },
    }
            response = requests.post(url, headers=headers, data=json.dumps(body)).json()
           
            if "name" in response and response["name"] == "UNPROCESSABLE_ENTITY":
                return Response(
                    {
                        "success": False,
                        "error": response["name"],
                        "details": response["details"][0]["description"],
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            if "error" in response and response["error"] == "invalid_client":
                return Response(
                    {
                        "success": False,
                        "error": response["error"],
                        "details": response["error_description"],
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
                
            user_wallet = Wallet.objects.get(user=request.user)
            payment_id = response["id"]
            
            transaction = Transaction(
                wallet=user_wallet,
                transaction_type="Deposit",
                status="Failed",
                amount=amount,
                payment_id=payment_id,
            )
            transaction.save()
            approve_payment = response["links"][1]["href"]
            return Response(
                {
                    "success": True,
                    "approval_url": approve_payment,
                },
                status=status.HTTP_200_OK,
            )
            
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        
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

class PaypalPaymentCallback(APIView):
    def get(self, request):
        try:
            payment_id = request.GET.get("token")
            print("payment_id",payment_id)
            transaction = Transaction.objects.get(payment_id=payment_id)

            url = f"{dowell_paypal_url}/v2/checkout/orders/{payment_id}"
            print("url",url)
            client_id = os.getenv("PAYPAL_CLIENT_ID", None)
            client_secret = os.getenv("PAYPAL_SECRET_KEY", None)
            encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {encoded_auth.decode()}",
                "Prefer": "return=representation",
            }
            response = requests.get(url, headers=headers).json()
            print("response",response)

            try:
                if response["name"] == "RESOURCE_NOT_FOUND":
                    redirect_url = f"https://100088.pythonanywhere.com/api/success"
                    response = HttpResponseRedirect(redirect_url)
                    return response
            except:
                pass
            try:
                if response["error"] == "invalid_client":
                    redirect_url = f"https://100088.pythonanywhere.com/api/success"
                    response = HttpResponseRedirect(redirect_url)
                    return response
            except:
                payment_status = response["status"]
                if payment_status == "APPROVED":
                    amount = response["purchase_units"][0]["amount"]["value"]
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

    def send_transaction_email(self, user_name, user_email, amount):
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

    def send_transaction_email(self, user_name, user_email, amount):
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


"""

GET TRANSACTIONS HISTORY

"""


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve the user's transaction history
        user = request.user
        transactions = Transaction.objects.filter(wallet__user=user).order_by(
            "-timestamp"
        )

        # Format the transaction history into a statement (you can customize the format)
        statement = "Transaction History:\n\n"
        for transaction in transactions:
            statement += f"Transaction Type: {transaction.transaction_type}\n"
            statement += f"Amount: ${transaction.amount}\n"
            statement += f"Status: {transaction.status}\n"
            statement += f"Timestamp: {transaction.timestamp}\n\n"

        # Send the statement to the user's email using your email API
        user_name = user.username
        user_email = user.email
        amount = sum(
            transaction.amount for transaction in transactions
        )  # Total amount in the statement
        email_api_url = f"https://100085.pythonanywhere.com/api/email/"

        email_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your Transaction History</title>
            </head>
            <body>
                <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                    <p style="font-size: 1.1em; text-align: center;">Dear {name},</p>
                    <p style="font-size: 1.1em; text-align: center;">Here is your transaction history:</p>
                    <pre>{statement}</pre>
                </div>
            </body>
            </html>
        """.format(
            name=user_name, statement=statement
        )

        payload = {
            "toname": user_name,
            "toemail": user_email,
            "subject": "Transaction History",
            "email_content": email_content,
        }

        response = requests.post(email_api_url, json=payload)
        print(response)
        if response.status_code == 200:
            return Response(
                {"message": "Transaction history sent to your email"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Failed to send transaction history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


"""

MAKE PAYMENTS TO EXTERNAL SITES

"""


class ExternalPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExternalPaymentSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            data = serializer.validated_data
            amount = data["amount"]
            # Get the wallet password from the request data
            wallet_password = request.data.get("wallet_password")

            # Verify the wallet password
            if not check_password(str(wallet_password), user.wallet.password):
                return Response(
                    {"message": "Incorrect wallet password"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            try:
                user_wallet = Wallet.objects.get(user=user)

                if user_wallet.balance >= amount:
                    # Deduct the payment amount from the user's wallet balance
                    user_wallet.balance -= Decimal(amount)
                    user_wallet.save()

                    # Create a transaction record
                    transaction = Transaction(
                        wallet=user_wallet,
                        transaction_type="Payment",
                        status="Completed",
                        amount=amount,
                    )
                    transaction.save()

                    # Pass the correct user object to the email function
                    self.send_transaction_email(user, amount)

                    return Response(
                        {"message": "Payment successful"}, status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"message": "Insufficient wallet balance"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Wallet.DoesNotExist:
                return Response(
                    {"message": "User does not have a wallet"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_transaction_email(self, user, amount):
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
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {name},</p>
                                <p style="font-size: 1.1em; text-align: center;">Your Payment of ${amount} to Dowell was successful.</p>
                                <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
                            </div>
                        </body>
                        </html>
                        """

        email_content = EMAIL_FROM_WEBSITE.format(name=name, amount=amount)
        payload = {
            "toname": name,
            "toemail": user.email,
            "subject": "Wallet Payment",
            "email_content": email_content,
        }
        response = requests.post(url, json=payload)
        print(response.text)
        return response.text


"""

USERPROFILE

"""


class UserProfileDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(user_profile)

        # Get user's email
        email = request.user.email

        # Assuming UserProfile has a ForeignKey relationship to Wallet
        wallet = user.wallet
        # Get wallet account number
        account_no = wallet.account_no if wallet else None

        # Add email and account_no to the serialized data
        serialized_data = serializer.data
        serialized_data["email"] = email
        serialized_data["account_no"] = account_no

        return Response(
            {"success": True, "data": serialized_data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        user_profile = UserProfile.objects.get(user=request.user)

        data = request.data
        if not data:
            return Response(
                {"success": False, "error": "Request body can't be empty"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # You can validate and update the user profile data here.
        serializer = UserProfileSerializer(user_profile, data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "user profile successfully updated",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


"""

DELETE USER ACCOUNT

"""


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        password = request.data.get("password")
        if not user.check_password(password):
            return Response(
                {"detail": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        # Log out the user
        logout(request)
        return Response(
            {"detail": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


"""

DEACTIVATE ACCOUNT


"""


class RequestDisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        # Generate a TOTP key for the user
        totp_key = self.generate_totp_key()
        # Save the TOTP key to the user's profile
        user_profile.totp_key = totp_key
        user_profile.save()
        # Send the TOTP key to the user via email or other communication method
        self.send_otp_email(user, totp_key)

        return Response(
            {"Message": "OTP for Account disable sent to your email."},
            status=status.HTTP_204_NO_CONTENT,
        )

    def generate_totp_key(self):
        # Generate a random secret key as bytes
        secret_key_bytes = secrets.token_bytes(20)  # 20 bytes (160 bits)
        # Convert the bytes to a base32-encoded string
        secret_key = base64.b32encode(secret_key_bytes).decode("utf-8")
        # Calculate the expiration time (30 minutes from now)
        expiration_time = timezone.now() + timezone.timedelta(minutes=30)
        # Create a TOTP instance
        totp = TOTP(
            secret_key, interval=30
        )  # Replace 'your-secret-key' with your secret key
        # Generate the TOTP token
        totp_key = totp.now()
        return totp_key

    def send_otp_email(self, user, totp_key):
        # API endpoint to send the email
        url = f"https://100085.pythonanywhere.com/api/email/"
        name = user.username
        expiration_time = timezone.now() + timezone.timedelta(
            minutes=30
        )  # 30 minutes from now
        EMAIL_FROM_WEBSITE = """
                    <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Account Disabling OTP</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 2; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
                                <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
                                <p style="font-size: 1.1em; text-align: center;">Dear {name}, you have requested an OTP to disable your account. Please enter the OTP below to proceed with the account disabling process.</p>
                                <p style="font-size: 1.1em; text-align: center;">Your OTP for account disabling is: {totp}</p>
                                <p style="font-size: 1.1em; text-align: center;">This OTP is valid until {expiration_time}.</p>
                                <p style="font-size: 1.1em; text-align: center;">If you did not request this action, you can ignore this email.</p>
                            </div>
                        </body>
                        </html>
                    """
        context = {"name": name, "totp": totp_key}

        email_content = EMAIL_FROM_WEBSITE.format(
            name=name, expiration_time=expiration_time, totp=totp_key
        )
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


class DisableAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        otp_key = request.data.get("otp_key")
        user = request.user
        if user:
            totp_key_from_profile = user.userprofile.totp_key
            if totp_key_from_profile == otp_key:
                # Disable the user
                user.is_active = False
                user.save()
                return Response(
                    {"Message": "Account temporarily disabled."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


# # class MoneyRequestView(APIView):
# #     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # Get the account_no from the request data
#         account_no = request.data.get("account_no")
#         # Try to find the wallet associated with the provided account_no
#         wallet = get_object_or_404(Wallet, account_no=account_no)

#         # Check if the wallet is associated with a user
#         receiver = (
#             wallet.user
#         )  # Assuming 'user' is the related name in your Wallet model
#         receiver_name = receiver.username
#         receiver_email = receiver.email

#         # Check if the receiver exists
#         if receiver:
#             # Ensure that the sender and receiver are not the same user
#             if request.user == receiver:
#                 return Response(
#                     {"detail": "You cannot request money from yourself."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             sender = request.user
#             sender_name = sender.username
#             sender_email = sender.email
#             amount = Decimal(request.data.get("amount"))

# #             # Generate a custom_id here
# #             custom_id = get_random_string(length=10)

#             # Create a new money request
#             serializer = MoneyRequestSerializer(
#                 data={
#                     "custom_id": custom_id,
#                     "sender": request.user.id,
#                     "receiver": receiver.id,
#                     "wallet": wallet.id,
#                     "amount": amount,
#                 }
#             )

#             if serializer.is_valid():
#                 serializer.save()
#                 self.sender_email(sender_name, sender_email, receiver_name, amount)
#                 self.receiver_email(sender_name, receiver_name, receiver_email, amount)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)

#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response(
#                 {"detail": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND
#             )

#     def sender_email(self, sender_name, sender_email, receiver_name, amount):
#         # API endpoint to send the email
#         url = f"https://100085.pythonanywhere.com/api/email/"
#         EMAIL_FROM_WEBSITE = """
#             <!DOCTYPE html>
#             <html lang="en">
#             <head>
#                 <meta charset="UTF-8">
#                 <meta http-equiv="X-UA-Compatible" content="IE-edge">
#                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                 <title>Your Wallet Transaction Confirmation</title>
#             </head>
#             <body>
#                 <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
#                     <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
#                     <p style="font-size: 1.1em; text-align: center;">Dear {sender_name},</p>
#                     <p style="font-size: 1.1em; text-align: center;">You have sent a request of ${amount} to {receiver_name}.</p>
#                     <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
#                 </div>
#             </body>
#             </html>
#         """

#         email_content = EMAIL_FROM_WEBSITE.format(
#             sender_name=sender_name, amount=amount, receiver_name=receiver_name
#         )

# #         payload = {
# #             "toname": sender_name,
# #             "toemail": sender_email,
# #             "subject": f"Sent Money request to {receiver_name}",
# #             "email_content": email_content,
# #         }
# #         response = requests.post(url, json=payload)
# #         print(response.text)
# #         return response.text

# #     def receiver_email(self, sender_name, receiver_name, receiver_email, amount):
# #         # API endpoint to send the email
# #         url = f"https://100085.pythonanywhere.com/api/email/"
# #         EMAIL_FROM_WEBSITE = """
# #             <!DOCTYPE html>
# #             <html lang="en">
# #             <head>
# #                 <meta charset="UTF-8">
# #                 <meta http-equiv=X-UA-Compatible content="IE-edge">
# #                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
# #                 <title>Your Wallet Transaction Confirmation</title>
# #             </head>
# #             <body>
# #                 <div style="font-family: Helvetica, Arial, sans-serif; min-width: 100px; overflow: auto; line-height: 1.6; margin: 50px auto; width: 70%; padding: 20px 0; border-bottom: 1px solid #eee;">
# #                     <a href="#" style="font-size: 1.2em; color: #00466a; text-decoration: none; font-weight: 600; display: block; text-align: center;">Dowell UX Living Lab Wallet</a>
# #                     <p style="font-size: 1.1em; text-align: center;">Dear {receiver_name},</p>
# #                     <p style="font-size: 1.1em; text-align: center;">You have received a request of ${amount} from {sender_name}.</p>
# #                     <p style="font-size: 1.1em; text-align: center;">Thank you for using our platform.</p>
# #                 </div>
# #             </body>
# #             </html>
# #         """

#         email_content = EMAIL_FROM_WEBSITE.format(
#             sender_name=sender_name, amount=amount, receiver_name=receiver_name
#         )

# #         payload = {
# #             "toname": receiver_name,
# #             "toemail": receiver_email,
# #             "subject": f"Received Money request from {sender_name}",
# #             "email_content": email_content,
# #         }
# #         response = requests.post(url, json=payload)
# #         print(response.text)
# #         return response.text


# # class AcceptRequestView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         user = request.user
# #         wallet_password = request.data.get("wallet_password")

# #         if not check_password(str(wallet_password), user.wallet.password):
# #             return Response(
# #                 {"message": "Incorrect wallet password"},
# #                 status=status.HTTP_401_UNAUTHORIZED,
# #             )

#         custom_id = request.data.get("custom_id")

#         try:
#             money_request = MoneyRequest.objects.get(custom_id=custom_id)
#         except MoneyRequest.DoesNotExist:
#             return Response(
#                 {"success": False, "detail": "Money request not found."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         if money_request.receiver == request.user and not money_request.is_confirmed:
#             if money_request.receiver.wallet.balance < money_request.amount:
#                 return Response(
#                     {"success": False, "detail": "Insufficient balance."},
#                     status=status.HTTP_200_OK,
#                 )

# #             money_request.is_confirmed = True
# #             money_request.save()

# #             money_request.receiver.wallet.balance -= money_request.amount
# #             money_request.receiver.wallet.save()

# #             money_request.sender.wallet.balance += money_request.amount
# #             money_request.sender.wallet.save()

# #             # Create a transaction record for the receiver
# #             receiver_transaction = Transaction(
# #                 wallet=money_request.receiver.wallet,
# #                 transaction_type="Sent from Request",
# #                 amount=money_request.amount,
# #                 status="Completed",
# #             )
# #             receiver_transaction.save()

# #             # Create a transaction record for the sender
# #             sender_transaction = Transaction(
# #                 wallet=money_request.sender.wallet,
# #                 transaction_type="Received from Request",
# #                 amount=money_request.amount,
# #                 status="Completed",
# #             )
# #             sender_transaction.save()

#             return Response(
#                 {
#                     "success": True,
#                     "detail": "Money request confirmed, and wallet balances updated.",
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {
#                     "success": False,
#                     "detail": "Money request not found or already confirmed.",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )


"""

DISPLAY ALL REQUESTS

"""


# class UserRequests(APIView):
#     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         user = request.user

#         # Filter confirmed and pending money requests and order by created_at in descending order
#         confirmed_requests = MoneyRequest.objects.filter(
#             receiver=user, is_confirmed=True
#         ).order_by("-created_at")
#         pending_requests = MoneyRequest.objects.filter(
#             receiver=user, is_confirmed=False
#         ).order_by("-created_at")

# #         # Serialize both sets of requests
# #         confirmed_serializer = MoneyRequestSerializer(confirmed_requests, many=True)
# #         pending_serializer = MoneyRequestSerializer(pending_requests, many=True)

#         return Response(
#             {
#                 "success": True,
#                 "data": {
#                     "confirmed_requests": confirmed_serializer.data,
#                     "pending_requests": pending_serializer.data,
#                 },
#             },
#             status=status.HTTP_200_OK,
#         )


class GetStripeSupporteCurrency(APIView):
    def get(self, request):
        return Response(
            {"success": True, "data": stripe_supported_currency},
            status=status.HTTP_200_OK,
        )


"""

DOWELL PAYMENTS

"""


class PaymentRequestView(APIView):
    serializer_class = DowellPaymentSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Create a transaction record with payment details
            payment_data = serializer.validated_data
            price = payment_data.get("price")
            currency = payment_data.get("currency")
            callback_url = payment_data.get("callback_url")

            unique_id = uuid.uuid4()
            initialization_id = str(unique_id)

            payment = PaymentInitialazation.objects.create(
                price=price,
                currency=currency,
                callback_url=callback_url,
                initialization_id=initialization_id,
            )
            payment.save()
            payment_info = {
                "price": price,
            }
            # Redirect user to login page with payment ID as request params
            redirect_url = f"https://dowell-wallet.vercel.app/payment-login/?initialization_id={initialization_id}&price={price}"

            return Response(
                {"redirect_url": redirect_url, "payment_info": payment_info},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentAuthoriazationView(APIView):
    serializer_class = PaymentAuthorizationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            initialization_id = serializer.validated_data.get("initialization_id")

            try:
                user = User.objects.get(email=email)

            except User.DoesNotExist:
                return Response(
                    {"success": False, "error": "Invalid credentials"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                try:
                    payment_initialization = PaymentInitialazation.objects.get(
                        initialization_id=initialization_id
                    )
                    price = Decimal(payment_initialization.price)
                    currency = payment_initialization.currency
                    callback_url = payment_initialization.callback_url

                    user_wallet = Wallet.objects.get(user=user)
                    user_balance = user_wallet.balance

                    if user_balance >= price:
                        # Deduct the amount from the user's wallet
                        user_wallet.balance -= price
                        user_wallet.save()

                        # Create a new Transaction entry
                        new_transaction = Transaction.objects.create(
                            wallet=user_wallet,
                            transaction_type="Dowell payment",
                            status="completed",
                            amount=price,
                            payment_id=payment_initialization,
                            session_id="",  # You might adjust this as per your needs
                        )

                        redirect_url = f"{callback_url}?id={payment_initialization}"
                        return Response(
                            {"redirect_url": redirect_url}, status=status.HTTP_200_OK
                        )
                    else:
                        return Response(
                            {"message": "Insufficient balance"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                except PaymentInitialazation.DoesNotExist:
                    return Response(
                        {"message": "Invalid payment initialization ID"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                except Wallet.DoesNotExist:
                    return Response(
                        {"message": "User wallet not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            else:
                return Response(
                    {"message": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentVerificationView(APIView):
    def post(self, request):
        data = request.data
        id = data["id"]
        try:
            obj = Transaction.objects.get(payment_id=id)
            print(obj)
            if obj.status == "completed":
                return Response(
                    {"success": True, "status": "completed"}, status=status.HTTP_200_OK
                )
            return Response(
                {"success": False, "status": "Failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as err:
            return Response(
                {"success": False, "status": "Failed", "message": f"{err}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
