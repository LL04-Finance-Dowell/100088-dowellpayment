# urls.py
from django.urls import path
from .views import UserRegistrationView, UserLoginView

urlpatterns = [
    # Other API routes...
    path('wallet/register/', UserRegistrationView.as_view(), name='register'),
    path('wallet/login/', UserLoginView.as_view(), name='login'),
]
