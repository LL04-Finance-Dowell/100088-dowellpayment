from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
   price = serializers.IntegerField()
   currency_code = serializers.CharField()
   product = serializers.CharField(required=False)
   
