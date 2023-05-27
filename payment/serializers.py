from rest_framework import serializers

class WorkflowPaymentSerializer(serializers.Serializer):
   #price = serializers.IntegerField()
   currency_code = serializers.CharField()
   product = serializers.CharField()
   quantity = serializers.CharField()


class OtherPaymentSerializer(serializers.Serializer):
   #price = serializers.IntegerField()
   currency_code = serializers.CharField()
   product = serializers.CharField()
   quantity = serializers.CharField()

   
class PaySerializer(serializers.Serializer):
   price = serializers.IntegerField()
  
