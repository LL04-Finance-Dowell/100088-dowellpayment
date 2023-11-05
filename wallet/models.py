from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import uuid


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100,null=True, blank=True)
    lastname = models.CharField(max_length=100,null=True, blank=True)
    profile_picture = models.ImageField(
        default="profile_images/avatar.jpg",
        upload_to="profile_images",  # dir to store the image
        null=True,
        blank=True,
    )
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    totp_key = models.CharField(max_length=16)

    def save(self, *args, **kwargs):
        # Call the super method to save the profile
        super().save(*args, **kwargs)

        # Resize the image after saving and use the URL-based file path
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)

class Wallet(models.Model):
    account_no = models.CharField(max_length=32, null=True, default="", unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.account_no:
            # Generate a unique wallet ID (e.g., UUID4) when creating a new wallet
            self.account_no = str(uuid.uuid4().hex)

        super(Wallet, self).save(*args, **kwargs)

    def __str__(self):
        return self.account_no



class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)
    status = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=10, blank=True, null=True)
    session_id = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user}"
