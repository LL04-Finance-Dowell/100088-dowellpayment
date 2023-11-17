from django.contrib import admin
from .models import Wallet, Transaction, UserProfile, MoneyRequest

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(UserProfile)
admin.site.register(MoneyRequest)
