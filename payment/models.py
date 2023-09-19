from django.db import models

# Create your models here.


class YapilyPaymentId(models.Model):
    payment_idempotency_id = models.CharField(max_length=50, blank=True, null=True)
    payment_id = models.CharField(max_length=50, blank=True, null=True)
    consent_token = models.CharField(max_length=150, blank=True, null=True)
    bank_id = models.CharField(max_length=50, blank=True, null=True)
    amount = models.CharField(max_length=50, blank=True, null=True)
    currency_code = models.CharField(max_length=50, blank=True, null=True)

    payment_type = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    desc = models.CharField(max_length=50, blank=True, null=True)
    date = models.CharField(max_length=50, blank=True, null=True)
    country_code = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(
        max_length=10, default="Initialized", blank=True, null=True
    )
    mail_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_idempotency_id
