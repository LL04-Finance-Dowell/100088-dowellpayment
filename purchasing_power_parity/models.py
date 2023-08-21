from django.db import models

# Create your models here.


class PPPCalculation(models.Model):
    country_name = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=100)
    world_bank_ppp = models.FloatField()
    # usd_exchange_rate = models.FloatField()

    def __str__(self):
        return self.country_name