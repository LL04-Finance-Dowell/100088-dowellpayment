from django.db import models

# Create your models here.

class WorkFlowAI(models.Model):
    country_name = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=100)
    price = models.FloatField()
    price_for_100_doc = models.FloatField()
    price_for_1000_doc = models.FloatField()
    price_for_2000_doc = models.FloatField()
    price_for_1_to_5_member_doc = models.FloatField()
    price_for_6_to_10_member_doc = models.FloatField()
    price_for_11_to_100_member_doc = models.FloatField()
    price_for_template_development = models.FloatField()
    
    def __str__(self):
        return self.country_name
