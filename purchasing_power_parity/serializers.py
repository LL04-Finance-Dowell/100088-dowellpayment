from rest_framework import serializers
from .models import PPPCalculation


class CurrencyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPPCalculation
        #get only the currency_name and country_name
        fields = ["currency_name", "country_name"]


class PPPSerializer(serializers.Serializer):
    base_currency = serializers.CharField()
    base_price = serializers.CharField()
    base_country = serializers.CharField()
    target_country = serializers.CharField()
    target_currency = serializers.CharField()
