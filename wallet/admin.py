from django.contrib import admin
from .models import (
    Wallet,
    Transaction,
    UserProfile,
    MoneyRequest,
    PaymentInitialazation,
    Wallets,
    UserInfo,
    Transactions
)

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(UserProfile)
admin.site.register(MoneyRequest)
admin.site.register(PaymentInitialazation)

admin.site.register(Wallets)
admin.site.register(UserInfo)
admin.site.register(Transactions)
