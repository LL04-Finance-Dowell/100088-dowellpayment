from django.urls import path
from . import views

urlpatterns = [
    #wallet url
    path('wallet_detail/',views.WalletDetailView.as_view(),name='wallet_detail'),
    #accounts urls
    path('signup/',views.UserRegistrationView.as_view(), name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout',views.logoutuser,name='logout'),
    path('verify-otp/', views.OTPVerificationView.as_view(), name='verify-otp'),
    #stripe url
    path('stripe-deposit/', views.StripePayment.as_view(),name="stripe-deposit"),
    path('stripe-callback',views.StripePaymentCallback.as_view())
]