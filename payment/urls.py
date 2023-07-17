from django.urls import path
from .views import (
    PaypalPayment,
    StripePayment,
    PaypalPaymentLink,
    StripePaymentLink,
    PaypalPaymentForTeam,
    StripePaymentForTeam,
    PaypalPaymentLinkForTeam,
    StripePaymentLinkForTeam,
    Success,
    Error,
    stripe_webhook,
    paypal_webhook,
    sending,
)

urlpatterns = [
    path("paypal/<str:api_key>", PaypalPayment.as_view()),
    path("stripe/<str:api_key>", StripePayment.as_view()),
    path("paypal/link/<str:api_key>", PaypalPaymentLink.as_view()),
    path("stripe/link/<str:api_key>", StripePaymentLink.as_view()),
    path("success", Success.as_view()),
    path("error", Error.as_view()),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    path("paypal/webhook/", paypal_webhook, name="paypal_webhook"),
    path("paypal", PaypalPaymentForTeam.as_view()),
    path("stripe", StripePaymentForTeam.as_view()),
    path("paypal/link", PaypalPaymentLinkForTeam.as_view()),
    path("stripe/link", StripePaymentLinkForTeam.as_view()),
    path("send_mail", sending, name="send_mail"),
]
