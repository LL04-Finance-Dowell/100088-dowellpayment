from rest_framework import serializers
from .models import TransactionDetail


class TransactionSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetail
        fields = "__all__"


class PaymentSerializer(serializers.Serializer):
    price = serializers.IntegerField()
    product = serializers.CharField()
    currency_code = serializers.CharField()


class StripePaymentLinkSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    price = serializers.IntegerField()
    product = serializers.CharField()
    currency_code = serializers.CharField()


class PaypalPaymentLinkSerializer(serializers.Serializer):
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    price = serializers.IntegerField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
