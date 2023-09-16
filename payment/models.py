from django.db import models

# Create your models here.


class YapilyPaymentId(models.Model):
    payment_id = models.CharField(max_length=50)
    user_uuid = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.payment_id
