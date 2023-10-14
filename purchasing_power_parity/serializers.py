from rest_framework import serializers
from .models import PPPCalculation


class CurrencyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = PPPCalculation
        # get only the currency_name and country_name
        fields = ["currency_name", "country_name"]


# class CurrencyNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PPPCalculation
#         # Include the desired fields
#         fields = ["currency_name", "country_name"]

#     def to_representation(self, instance):
#         # Get the queryset for PPPCalculation and apply distinct to currency_name
#         queryset = PPPCalculation.objects.values('currency_name').distinct()

#         # Serialize the queryset using the serializer
#         serialized_data = self.fields['currency_name'].to_representation(queryset)

#         # Return the serialized data
#         return serialized_data


class PPPSerializer(serializers.Serializer):
    base_currency = serializers.CharField()
    base_price = serializers.CharField()
    base_country = serializers.CharField()
    target_country = serializers.CharField()
    target_currency = serializers.CharField()


# class CurrencyNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PPPCalculation
#         fields = ["currency_name", "country_name","unique_currency_names"]

#     unique_currency_names = serializers.SerializerMethodField()

#     def get_unique_currency_names(self, obj):
#         # Assuming you have a queryset 'queryset' with the relevant data
#         unique_currency_names = PPPCalculation.objects.all().values_list("currency_name", flat=True).distinct()
#         # return unique_currency_names
#          # Format the unique currency names as a list of dictionaries
#         formatted_currency_names = [{"currency_name": name} for name in unique_currency_names]

#         return formatted_currency_names
