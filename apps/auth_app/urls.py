from django.urls import path
from .views import (
    AdminLoginView,
    SendOTPView,
    VerifyOTPView,
    MeView,
    LogoutView,
)

urlpatterns = [
    path('admin-login/', AdminLoginView.as_view()),
    path('send-otp/',    SendOTPView.as_view()),
    path('verify-otp/',  VerifyOTPView.as_view()),
    path('me/',          MeView.as_view()),
    path('logout/',      LogoutView.as_view()),
]