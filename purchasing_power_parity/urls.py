from django.urls import path
from .views import GetPurchasingPowerParity


urlpatterns = [
    path("", GetPurchasingPowerParity.as_view()),
]
