from rest_framework import serializers
from .models import PPPCalculation


# class UppercaseCharField(serializers.CharField):
#     def to_internal_value(self, data):
#         return super().to_internal_value(data.upper())

class CurrencyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPPCalculation
        fields = ["currency_name"]

class PPPSerializer(serializers.Serializer):
    base_currency = serializers.CharField()
    base_price = serializers.CharField()
    base_country = serializers.CharField()
    target_country = serializers.CharField()
    target_currency = serializers.CharField()
