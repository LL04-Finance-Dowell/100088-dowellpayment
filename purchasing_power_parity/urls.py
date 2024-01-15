from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (
    GetPurchasingPowerParity,
    GetPublicPurchasingPowerParity,
    SendResponseToClient,
)


urlpatterns = [
    path("ppp", GetPurchasingPowerParity.as_view()),
    path("ppp/client-mail", SendResponseToClient.as_view()),
    path("ppp/public/<str:api_key>", GetPublicPurchasingPowerParity.as_view()),
    path("ppp/exchange-rates",views.GetExchangeRates.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
