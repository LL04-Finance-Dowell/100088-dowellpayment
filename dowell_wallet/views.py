from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login,logout
from .serializers import UserRegistrationSerializer,UserSerializer
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

@login_required(login_url='signup')
def WalletDetail(request):
    # Retrieve wallet balance and other data here
    wallet = get_object_or_404(Wallet, user=request.user)
    transactions = wallet.transaction_set.all()
    print(f"Logged-in user: {request.user.username}")
    print(wallet)
    print(transactions)
    context = {
        'wallet': wallet,
        'transactions':transactions
    }
    return render(request,'wallet-detail.html',context)

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



def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        url = "http://127.0.0.1:8000/wallet/login_api/"
        try:
            response = requests.post(url, data={
                'username': username,
                'password': password,
            })
            if response.status_code == 200:
                response_data = response.json()
                user_data = response_data.get('user')
                token = response_data.get('token')
                
                if user_data and 'username' in user_data:
                    try:
                        user = User.objects.get(username=user_data['username'])
                        login(request, user)
                        return redirect('wallet_detail')
                    except User.DoesNotExist:
                        return HttpResponse("User does not exist", status=400)
                else:
                    return HttpResponse("Invalid response from the login API", status=400)
        except RequestException as e:
            return HttpResponse("Error connecting to the login API", status=500)

    return render(request, 'signin.html')

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({'user': user_data, 'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
def logoutuser(request):
    logout(request)
    return redirect(reverse('signin'))

def sign_up(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        url ="http://127.0.0.1:8000/wallet/signup_api/" 
        response = requests.post(url, data={
            'username':username,
            'password':password,
            'email':email,
        })
        if response.status_code == 201:
            # Registration was successful
            login_url = response.json().get('login_url')
            return redirect(reverse('signin'))
    return render(request, 'signup.html')

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            user.save()
            # Check if a Wallet already exists for the user
            wallet, created = Wallet.objects.get_or_create(user=user)
            if created:
                # Wallet was created
                pass
            return Response({"detail": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
