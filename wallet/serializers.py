from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Wallet,Transaction

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class WalletDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ('balance',)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


