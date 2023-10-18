from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login,logout
from .serializers import UserRegistrationSerializer,UserSerializer,WalletDetailSerializer, TransactionSerializer
from django.contrib.auth.models import User
from django.shortcuts import render,redirect, get_object_or_404,HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from requests.exceptions import RequestException
import requests
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Wallet,Transaction
from django.urls import reverse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode





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
                is_active=False  # Set the user as inactive until they verify their email.
            )
            user.save()
            print('account created for user')

            # Generate a verification token for the user
            verification_token = default_token_generator.make_token(user)
            print(verification_token)
            # Send a verification email to the user
            self.send_verification_email(user, verification_token, request)
             # Check if a Wallet already exists for the user
            wallet, created = Wallet.objects.get_or_create(user=user)
            if created:
                # Wallet was created
                pass
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'message': 'Please check your email for verification instructions.','access_token': access_token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user, token, request):
        current_site = get_current_site(request)
        print(current_site)
        mail_subject = 'Activate your account'
        message = render_to_string('verification_email.html', {
            'user': user,
            'domain': current_site.domain,
            'token': token,
        })
        from_email = settings.EMAIL_HOST_USER
        print(from_email)
        to_email = user.email
        send_mail(mail_subject, message, from_email, [to_email])

class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({'message': 'Your email has been verified.'}, status=status.HTTP_200_OK)
            return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


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
    
