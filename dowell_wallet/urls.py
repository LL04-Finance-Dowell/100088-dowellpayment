from django.urls import path
from . import views

urlpatterns = [
    #wallet url
    path('wallet_detail',views.WalletDetail,name='wallet_detail'),
    #accounts urls
    path('signin/', views.signin, name='signin'),
    path('signup/',views.sign_up, name="signup"),
    path('signup_api/',views.UserRegistrationView.as_view()),
    path('login_api/',views.LoginView.as_view()),
    path('logout',views.logoutuser,name='logout'),
    #stripe url
    path('stripe-deposit', views.stripe_deposit,name="stripe-deposit"),
]