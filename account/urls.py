from django.urls import path

from .views import (
    UserSignUpAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    RotateAccessTokenAPIView,
    ResetPasswordAPIView,
    ForgotPasswordAPIView,
    ChangePasswordAPIView,
    VerifyEmailAddressAPIView,
    ResendVerificationEmailAPIView
)

app_name = "account"

urlpatterns = [
    path("signup/", UserSignUpAPIView.as_view(), name="user-signup"),
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("rotate-token/", RotateAccessTokenAPIView.as_view(), name="rotate-token"),
    path("forget-password/", ForgotPasswordAPIView.as_view(), name="forget-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("verify-email/", VerifyEmailAddressAPIView.as_view(), name='verify-email'),
    path("resend-verification-email/", ResendVerificationEmailAPIView.as_view(), name="resend-verification-email")
]

