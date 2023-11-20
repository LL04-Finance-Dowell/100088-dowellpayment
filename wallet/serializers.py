from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Wallet, Transaction, UserProfile, MoneyRequest
from django.utils.crypto import get_random_string


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class WalletDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = "__all__"


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
        If it has a decimal portion, it keeps it (preserving the decimal part).

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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class MoneyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyRequest
        fields = "__all__"


class DowellPaymentSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=10)
    callback_url = serializers.URLField()


class PaymentVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)
    payment_id = serializers.CharField(max_length=10)