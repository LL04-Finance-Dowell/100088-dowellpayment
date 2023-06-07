from django.urls import path
from .views import PaypalPayment,StripePayment,PaypalPaymentLink,StripePaymentLink

urlpatterns = [
    path('paypal',PaypalPayment.as_view()),
    path('stripe',StripePayment.as_view()),
    path('paypal/link',PaypalPaymentLink.as_view()),
    path('stripe/link',StripePaymentLink.as_view()),
]