from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login,logout
from .serializers import UserRegistrationSerializer,UserSerializer,WalletDetailSerializer, TransactionSerializer
from django.contrib.auth.models import User
from .models import UserProfile
from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from requests.exceptions import RequestException
import requests
import base64
import secrets
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Wallet,Transaction
from django.urls import reverse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from pyotp import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes



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
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                is_active = False,
            )
            user.save()
            print(f'account created for {user}')
            # Generate a verification token for the user
            verification_token = default_token_generator.make_token(user)
            print(verification_token)
            # Encode the user's ID
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            # Generate a TOTP key for the user
            totp_key = self.generate_totp_key()
            # Create the user profile with totp_key
            UserProfile.objects.create(user=user, totp_key=totp_key)
            print(totp_key)
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
            return Response({'message': 'Please check your email for verification instructions.', 'access_token': access_token,"uidb64":uidb64,"verification_token":verification_token}, status=status.HTTP_201_CREATED)
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
        return totp_key

    def send_verification_email(self, user, totp_key, request):
        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        domain = current_site.domain
        message = (
            f'Hello {user.username},\n\n'
            f'Thank you for signing up on our platform. To verify your email address, please use the following one-time code within 30 minutes:\n'
            f'{totp_key}\n\n'
            f'If you didn\'t create an account on our platform, you can ignore this email.'
        )
        from_email = settings.EMAIL_HOST_USER
        to_email = user.email
        send_mail(mail_subject, message, from_email, [to_email])

@method_decorator(csrf_exempt, name='dispatch')
class OTPVerificationView(APIView):
    def post(self, request):
        totp_key = request.data.get('otp_key')
        uidb64 = request.data.get('uidb64')
        token = request.data.get('verification_token')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        totp_key_from_profile = user.userprofile.totp_key
        if totp_key_from_profile == totp_key:
            # Activate the user
            user.is_active = True
            user.save()
            return Response({'message': 'Account verified and activated.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid OTP or token.'}, status=status.HTTP_400_BAD_REQUEST)



class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        transactions = Transaction.objects.filter(wallet=wallet)
        wallet_serializer = WalletDetailSerializer(wallet)
        transactions_serializer = TransactionSerializer(transactions, many=True)

        data = {
            'wallet': wallet_serializer.data,
            'transactions': transactions_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)

def stripe_deposit(request):
    stripe_key = settings.STRIPE_KEY
    if request.method == "POST":
        amount = request.POST.get("amount")
        # Update the wallet balance after a successful payment
        user_wallet = Wallet.objects.get(user=request.user)
        user_wallet.balance += int(amount)
        user_wallet.save()
        transaction = Transaction(wallet=user_wallet, transaction_type='Deposit', amount=amount)
        transaction.save()
        return redirect(reverse('wallet_detail'))
    context ={
        "stripe_key":stripe_key
    }
    return render(request,'deposit.html',context)
    
