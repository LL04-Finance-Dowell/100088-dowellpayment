from rest_framework import serializers


class UppercaseCharField(serializers.CharField):
    def to_internal_value(self, data):
        return super().to_internal_value(data.upper())


class PPPSerializer(serializers.Serializer):
    base_currency = UppercaseCharField()
    base_price = serializers.CharField()
    base_country = serializers.CharField()
    target_country = serializers.CharField()
    target_currency = UppercaseCharField()
