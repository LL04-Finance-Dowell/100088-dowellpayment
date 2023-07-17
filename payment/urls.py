from django.urls import path
from .views import (
    PaypalPayment,
    StripePayment,
    VerifyPaypalPayment,
    VerifyStripePayment,
    GenerateStripePaymentLink,
    VerifyStripePaymentLink,
    Success,
    Error,
    stripe_webhook,
    paypal_webhook,
    sending,
)

urlpatterns = [
    path("stripe/initialize/<str:api_key>", StripePayment.as_view()),
    path("verify/payment/stripe/<str:api_key>", VerifyStripePayment.as_view()),
    path("generate/stripe/link/<str:api_key>", GenerateStripePaymentLink.as_view()),
    path("verify/stripe/link/<str:api_key>", VerifyStripePaymentLink.as_view()),
    path("paypal/initialize/<str:api_key>", PaypalPayment.as_view()),
    path("verify/payment/paypal/<str:api_key>", VerifyPaypalPayment.as_view()),
    path("success", Success.as_view()),
    path("error", Error.as_view()),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    path("paypal/webhook/", paypal_webhook, name="paypal_webhook"),
    # path('team/paypal/initialize',PaypalPaymentForTeam.as_view()),
    # path('team/stripe/initialize',StripePaymgenerateentForTeamInitialize.as_view()),
    # path('team/stripe/versend_mailify',TeamPaymentVerify.as_view()),
    # path('team/paypal/link',PaypalPaymentLinkForTeam.as_view()),
    # path('team/stripe/link',StripePaymentLinkForTeam.as_view()),
    # path('send_mail',sending, name="send_mail"),
]
