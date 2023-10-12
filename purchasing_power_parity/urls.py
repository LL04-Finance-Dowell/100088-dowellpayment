from django.urls import path
from .views import GetCurrencyNameAndCountryName, GetPurchasingPowerParity, GetPublicPurchasingPowerParity


urlpatterns = [
    path("country-currency", GetCurrencyNameAndCountryName.as_view()),
    path("ppp", GetPurchasingPowerParity.as_view()),
    path("ppp/public/<str:api_key>", GetPublicPurchasingPowerParity.as_view()),
]
