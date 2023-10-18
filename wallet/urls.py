from django.urls import path
from . import views

urlpatterns = [
    #wallet url
    path('wallet_detail',views.WalletDetailView.as_view(),name='wallet_detail'),
    #accounts urls
    path('signup',views.UserRegistrationView.as_view(), name='register'),
    path('login',views.LoginView.as_view(),name='login'),
    path('logout',views.logoutuser,name='logout'),
    path('verify-email',views.EmailVerificationView.as_view()),
    #stripe url
    path('stripe-deposit', views.stripe_deposit,name="stripe-deposit"),
]