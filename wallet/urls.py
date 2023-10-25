from django.urls import path
from . import views

urlpatterns = [
    # wallet url
    path("wallet_detail", views.WalletDetailView.as_view(), name="wallet_detail"),
    path('transactions-history',views.TransactionHistoryView.as_view(),name="transactions-history"),
    # accounts urls
    path("signup", views.UserRegistrationView.as_view(), name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path('logout',views.LogoutView.as_view(),name="logout"),
    path('resend-otp', views.ResendOTPView.as_view(), name='resend-otp'),
    path("verify-email", views.OTPVerificationView.as_view()),
    path('request-reset-password', views.PasswordResetRequestView.as_view(), name='request-reset-password'),
    path('verify-password-otp', views.ResetPasswordOtpVerify.as_view()),
    path('reset-password', views.PasswordResetView.as_view(), name='reset-password'),
    # stripe url
    path("stripe-payment", views.StripePayment.as_view(), name="stripe-payment"),
    path(
        "stripe-callback",
        views.StripePaymentCallback.as_view(),
        name="verify-stripe-payment",
    ),
    #transfer url
    path("transfer",views.SendMoney.as_view(),name="transfer"),
    #external payment
    path('external-payment',views.ExternalPaymentView.as_view(),name="external-payment"),
    #userprofile
    path('profile',views.UserProfileDetail.as_view(),name="profile"),

]
