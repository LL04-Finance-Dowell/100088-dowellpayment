from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Wallet, Transaction


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phone_number = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'firstname', 'lastname', 'phone_number')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class WalletDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("balance",)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class PaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        amount = data.get("amount")

        """
        The code checks if the price has no decimal portion (price % 1 == 0) 
        and converts it to an integer if that's the case. 
        If it has a decimal portion, it keeps it as is (preserving the decimal part).

        """
        # print("actual price", amount)
        if amount % 1 == 0:
            data["amount"] = int(amount)
        else:
            data["amount"] = amount
        return data


class VerifyPaymentSerializer(serializers.Serializer):
    id = serializers.CharField()



class ExternalPaymentSerializer(serializers.Serializer):
    amount = serializers.FloatField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        amount = data.get("amount")

        """
        The code checks if the price has no decimal portion (price % 1 == 0) 
        and converts it to an integer if that's the case. 
        If it has a decimal portion, it keeps it as is (preserving the decimal part).

        """
        # print("actual price", amount)
        if amount % 1 == 0:
            data["amount"] = int(amount)
        else:
            data["amount"] = amount
        return data
