from rest_framework import serializers

   
class PaymentSerializer(serializers.Serializer):
   price = serializers.IntegerField()
   product = serializers.CharField()

  
