from django.db import models

# Create your models here.


class ExchangeRate(models.Model):
    country_name = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=100)
    usd_exchange_rate = models.FloatField()

    def __str__(self):
        return self.country_name


class TransactionDetail(models.Model):
    payment_id = models.CharField(max_length=200)
    session_id = models.CharField(max_length=500, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)
    date = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=100, blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    mail_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_id


class PubicTransactionDetail(models.Model):
    payment_id = models.CharField(max_length=200)
    session_id = models.CharField(max_length=500, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)
    date = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=100, blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    mail_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_id


class PaymentLinkTransaction(models.Model):
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    session_id = models.CharField(max_length=500, blank=True, null=True)
    amount = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)
    date = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=100, blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    mail_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_id


class BaseModel(models.Model):
    country_name = models.CharField(max_length=100)
    currency_name = models.CharField(max_length=100)
    currency_code = models.CharField(max_length=100)
    price = models.FloatField()

    class Meta:
        abstract = True


class WorkFlowAI(BaseModel):
    price_for_100_doc = models.FloatField()
    price_for_1000_doc = models.FloatField()
    price_for_2000_doc = models.FloatField()
    price_for_1_to_5_member_doc = models.FloatField()
    price_for_6_to_10_member_doc = models.FloatField()
    price_for_11_to_100_member_doc = models.FloatField()
    price_for_template_development = models.FloatField()

    def __str__(self):
        return self.country_name


class WifiQrcode(BaseModel):
    def __str__(self):
        return self.country_name


class DigitalQ(BaseModel):
    def __str__(self):
        return self.country_name


class LogoScan(BaseModel):
    def __str__(self):
        return self.country_name


class Nps(BaseModel):
    def __str__(self):
        return self.country_name


class Voc(BaseModel):
    def __str__(self):
        return self.country_name


class UxLive(BaseModel):
    def __str__(self):
        return self.country_name


class SocialMediaAutomation(BaseModel):
    def __str__(self):
        return self.country_name


class LicenseCompatibility(BaseModel):
    def __str__(self):
        return self.country_name
