from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )


class VerifyPaymentSerializer(serializers.Serializer):
    id = serializers.CharField()


class PublicStripeSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )


class VerifyPublicStripSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    id = serializers.CharField()


class PublicPaypalSerializer(serializers.Serializer):
    mode_choices = ("sandbox", "live")
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )
    mode = serializers.ChoiceField(choices=mode_choices)


class VerifyPublicPaypalSerializer(serializers.Serializer):
    MODE_CHOICES = ("sandbox", "live")
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    id = serializers.CharField()
    mode = serializers.ChoiceField(choices=MODE_CHOICES)
