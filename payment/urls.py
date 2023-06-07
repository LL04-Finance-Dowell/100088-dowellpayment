from django.urls import path
from .views import PaypalPayment,StripePayment

urlpatterns = [
    path('paypal',PaypalPayment.as_view()),
    path('stripe',StripePayment.as_view()),
]