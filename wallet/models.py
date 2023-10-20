from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    totp_key = models.CharField(max_length=16)

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)  # Assuming Wallet is related to this transaction
    transaction_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255)  # Define a status field
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255)  # Define a session_id field
    payment_id = models.CharField(max_length=255)  # Define a payment_id field

    # Add any other fields you need

    def __str__(self):
        return f"Transaction ID: {self.id}"
