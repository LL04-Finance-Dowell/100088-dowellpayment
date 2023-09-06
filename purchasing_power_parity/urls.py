from django.urls import path
from .views import GetPurchasingPowerParity, GetPublicPurchasingPowerParity


urlpatterns = [
    path("", GetPurchasingPowerParity.as_view()),
    path("public/<str:api_key>", GetPublicPurchasingPowerParity.as_view()),
]
