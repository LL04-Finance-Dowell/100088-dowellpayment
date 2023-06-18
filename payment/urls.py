from django.urls import path
from .views import PaypalPayment,StripePayment,PaypalPaymentLink,StripePaymentLink,Success,Error,stripe_webhook

urlpatterns = [
    path('paypal',PaypalPayment.as_view()),
    path('stripe',StripePayment.as_view()),
    path('paypal/link',PaypalPaymentLink.as_view()),
    path('stripe/link',StripePaymentLink.as_view()),
    path('success',Success.as_view()),
    path('error',Error.as_view()),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
]