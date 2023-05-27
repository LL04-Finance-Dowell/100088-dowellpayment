from django.urls import path
from .views import PaypalPayment,StripePaymentWorkflowAI,StripePaymentOther

urlpatterns = [
    path('paypal',PaypalPayment.as_view()),
    path('stripe/workflow',StripePaymentWorkflowAI.as_view()),
    path('stripe/other',StripePaymentOther.as_view()),
]