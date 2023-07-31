from django.urls import path
from .views import (
    PaypalPayment,
    StripePayment,
    VerifyPaypalPayment,
    VerifyStripePayment,
    StripePaymentPublic,
    VerifyStripePaymentPublic,
    PaypalPaymentPublic,
    VerifyPaypalPaymentPublic,
    Success,
    Error,
)

urlpatterns = [
    path("stripe/initialize", StripePayment.as_view()),
    path("verify/payment/stripe", VerifyStripePayment.as_view()),
    path("paypal/initialize", PaypalPayment.as_view()),
    path("verify/payment/paypal", VerifyPaypalPayment.as_view()),
    path("stripe/initialize/public/<str:api_key>", StripePaymentPublic.as_view()),
    path(
        "verify/payment/stripe/public/<str:api_key>",
        VerifyStripePaymentPublic.as_view(),
    ),
    path("paypal/initialize/public/<str:api_key>", PaypalPaymentPublic.as_view()),
    path(
        "verify/payment/paypal/public/<str:api_key>",
        VerifyPaypalPaymentPublic.as_view(),
    ),
    path("success", Success.as_view()),
    path("error", Error.as_view()),
]
