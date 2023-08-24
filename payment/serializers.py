from decimal import Decimal
from rest_framework import serializers


# SERIALIZERS FOR DOWELL INTERNAL TEAM


class PaymentSerializer(serializers.Serializer):
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    timezone = serializers.CharField(required=False, default=None, allow_blank=True)
    description = serializers.CharField(required=False, default=None, allow_blank=True)
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price = data.get("price")

        # if isinstance(price, str):
        #     # Convert the string back to a Decimal
        #     price = Decimal(price)
        discount_price = round(price - (0.4 * price), 2)

        if price % 1 == 0:
            data["price"] = int(discount_price)
        else:
            data["price"] = discount_price
        return data


class VerifyPaymentSerializer(serializers.Serializer):
    id = serializers.CharField()


# SERIALIZERS FOR WORKLOW AI INTERNAL TEAM
class WorkflowStripeSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    template_id = serializers.CharField()
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price = data.get("price")

        if price % 1 == 0:
            data["price"] = int(price)
        else:
            data["price"] = price
        return data


class WorkflowVerifyStripSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    id = serializers.CharField()


class WorkflowPaypalSerializer(serializers.Serializer):
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    template_id = serializers.CharField()
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price = data.get("price")

        if price % 1 == 0:
            data["price"] = int(price)
        else:
            data["price"] = price

        return data


class WorkflowVerifyPaypalSerializer(serializers.Serializer):
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    id = serializers.CharField()


# SERIALIZERS FOR PUBLIC USAGE
class PublicStripeSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price = data.get("price")

        if price % 1 == 0:
            data["price"] = int(price)
        else:
            data["price"] = price
        return data


class VerifyPublicStripSerializer(serializers.Serializer):
    stripe_key = serializers.CharField()
    id = serializers.CharField()


class PublicPaypalSerializer(serializers.Serializer):
    MODE_CHOICES = ("sandbox", "live")
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    price = serializers.FloatField()
    product = serializers.CharField()
    currency_code = serializers.CharField()
    callback_url = serializers.CharField(
        required=False, default="https://100088.pythonanywhere.com/api/success"
    )
    mode = serializers.CharField()

    def validate_mode(self, value):
        if value not in self.MODE_CHOICES:
            raise serializers.ValidationError(
                "Invalid mode. Must be 'sandbox' or 'live'."
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price = data.get("price")
        mode = data.get("mode")

        if price % 1 == 0:
            data["price"] = int(price)
        else:
            data["price"] = price

        if mode == "sandbox":
            data["public_paypal_url"] = "https://api-m.sandbox.paypal.com"
        elif mode == "live":
            data["public_paypal_url"] = "https://api-m.paypal.com"

        return data


class VerifyPublicPaypalSerializer(serializers.Serializer):
    MODE_CHOICES = ("sandbox", "live")
    paypal_client_id = serializers.CharField()
    paypal_secret_key = serializers.CharField()
    id = serializers.CharField()
    mode = serializers.CharField()

    def validate_mode(self, value):
        if value not in self.MODE_CHOICES:
            raise serializers.ValidationError(
                "Invalid mode. Must be 'sandbox' or 'live'."
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        mode = data.get("mode")

        if mode == "sandbox":
            data["public_paypal_url"] = "https://api-m.sandbox.paypal.com"
        elif mode == "live":
            data["public_paypal_url"] = "https://api-m.paypal.com"

        return data
