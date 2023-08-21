from django.urls import path
from .views import GetPurchasingPowerParity


urlpatterns = [
    path("get",GetPurchasingPowerParity.as_view()),
]