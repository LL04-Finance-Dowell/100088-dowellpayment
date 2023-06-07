from rest_framework import serializers

   
class PaymentSerializer(serializers.Serializer):
   price = serializers.IntegerField()
   product = serializers.CharField()
   
class StripePaymentLinkSerializer(serializers.Serializer):
   stripe_key = serializers.CharField()
   price = serializers.IntegerField()
   product = serializers.CharField()
   
class PaypalPaymentLinkSerializer(serializers.Serializer):
   paypal_client_id = serializers.CharField()
   paypal_secret_key = serializers.CharField()
   price = serializers.IntegerField()
   product = serializers.CharField()

  
