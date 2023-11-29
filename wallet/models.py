from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import random
from django.utils.crypto import get_random_string


class Wallets(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True, null=True)
    account_no = models.CharField(max_length=20, null=True, default="")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=100)
    password = models.CharField(
        max_length=4, null=True
    )  # Add a new field for wallet password

    def save(self, *args, **kwargs):
        if not self.account_no:
            # Generate a random 20-digit account number
            self.account_no = "".join([str(random.randint(0, 9)) for _ in range(20)])

        super(Wallets, self).save(*args, **kwargs)

    def __str__(self):
        return self.account_no


class UserInfo(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Transactions(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True, null=True)
    transaction_type = models.CharField(max_length=100)
    status = models.CharField(max_length=10, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=10, blank=True, null=True)
    session_id = models.CharField(max_length=10, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100,blank=True, null=True)
    firstname = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(
        default="profile_images/avatar.jpg",
        upload_to="profile_images",  # dir to store the image
        null=True,
        blank=True,
    )
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

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
    account_no = models.CharField(max_length=20, null=True, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    password = models.CharField(
        max_length=4, null=True
    )  # Add a new field for wallet password

    def save(self, *args, **kwargs):
        if not self.account_no:
            # Generate a random 20-digit account number
            self.account_no = "".join([str(random.randint(0, 9)) for _ in range(20)])

        super(Wallet, self).save(*args, **kwargs)

    def __str__(self):
        return self.account_no


class MoneyRequest(models.Model):
    custom_id = models.CharField(max_length=10, unique=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_money_requests"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_money_requests"
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MoneyRequest {self.custom_id}"

    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate a random 10-character custom ID
            self.custom_id = get_random_string(length=10)

        super(MoneyRequest, self).save(*args, **kwargs)


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


class PaymentInitialazation(models.Model):
    price = models.CharField(max_length=10)
    currency = models.CharField(max_length=10)
    callback_url = models.CharField(max_length=100)
    initialization_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.initialization_id}"
