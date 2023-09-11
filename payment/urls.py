from django.urls import path
from .views import (
    PaypalPayment,
    StripePayment,
    StripeQrcodePayment,
    PaypalQrcodePayment,
    VerifyPaypalPayment,
    VerifyStripePayment,
    WorkflowStripePayment,
    WorkflowStripeQrPayment,
    WorkflowVerifyStripePayment,
    WorkflowPaypalPayment,
    WorkflowPaypalQrPayment,
    WorkflowVerifyPaypalPayment,
    StripePaymentPublic,
    StripeQrPaymentPublic,
    VerifyStripePaymentPublic,
    PaypalPaymentPublic,
    PaypalQrPaymentPublic,
    VerifyPaypalPaymentPublic,
    StripePaymentPublicUse,
    StripeQrPaymentPublicUse,
    VerifyStripePaymentPublicUse,
    PaypalPaymentPublicUse,
    PaypalQrPaymentPublicUse,
    VerifyPaypalPaymentPublicUse,
    Success,
    Error,

    NetPaymentPlaid,
    NetPaymentYapily
)

urlpatterns = [
    path("stripe/initialize", StripePayment.as_view()),
    path("stripe/initialize/qrcode", StripeQrcodePayment.as_view()),
    path("verify/payment/stripe", VerifyStripePayment.as_view()),
    path("paypal/initialize", PaypalPayment.as_view()),
    path("paypal/initialize/qrcode", PaypalQrcodePayment.as_view()),
    path("verify/payment/paypal", VerifyPaypalPayment.as_view()),
    path("workflow/stripe/initialize", WorkflowStripePayment.as_view()),
    path("workflow/stripe/initialize/qrcode", WorkflowStripeQrPayment.as_view()),
    path("workflow/verify/payment/stripe", WorkflowVerifyStripePayment.as_view()),
    path("workflow/paypal/initialize", WorkflowPaypalPayment.as_view()),
    path("workflow/paypal/initialize/qrcode", WorkflowPaypalQrPayment.as_view()),
    path("workflow/verify/payment/paypal", WorkflowVerifyPaypalPayment.as_view()),
    path("stripe/initialize/public/<str:api_key>", StripePaymentPublic.as_view()),
    path(
        "stripe/initialize/qrcode/public/<str:api_key>", StripeQrPaymentPublic.as_view()
    ),
    path(
        "verify/payment/stripe/public/<str:api_key>",
        VerifyStripePaymentPublic.as_view(),
    ),
    path("paypal/initialize/public/<str:api_key>", PaypalPaymentPublic.as_view()),
    path(
        "paypal/initialize/qrcode/public/<str:api_key>", PaypalQrPaymentPublic.as_view()
    ),
    path(
        "verify/payment/paypal/public/<str:api_key>",
        VerifyPaypalPaymentPublic.as_view(),
    ),
    path("stripe/initialize/public-use", StripePaymentPublicUse.as_view()),
    path("stripe/initialize/qrcode/public-use", StripeQrPaymentPublicUse.as_view()),
    path(
        "verify/payment/stripe/public-use",
        VerifyStripePaymentPublicUse.as_view(),
    ),
    path("paypal/initialize/public-use", PaypalPaymentPublicUse.as_view()),
    path("paypal/initialize/qrcode/public-use", PaypalQrPaymentPublicUse.as_view()),
    path(
        "verify/payment/paypal/public-use",
        VerifyPaypalPaymentPublicUse.as_view(),
    ),
    path("success", Success.as_view()),
    path("error", Error.as_view()),

    path("plaid/initialize",NetPaymentPlaid.as_view()),
    path("yapily/initialize",NetPaymentYapily.as_view())
]
