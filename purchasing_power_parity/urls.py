from django.urls import path
from .views import GetPurchasingPowerParity, GetPublicPurchasingPowerParity


urlpatterns = [
    path("ppp", GetPurchasingPowerParity.as_view()),
    path("ppp/public/<str:api_key>", GetPublicPurchasingPowerParity.as_view()),
]
