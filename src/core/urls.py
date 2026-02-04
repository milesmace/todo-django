from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    CoreTodoGroupViewSet,
    CoreTodoViewSet,
    LoginView,
    LogoutView,
    RegisterView,
    RequestResetPasswordView,
    ResendVerificationEmailView,
    ResetPasswordView,
    TokenRefreshView,
    UserProfileView,
    VerifyEmailView,
)

router = DefaultRouter()
router.register(r"groups", CoreTodoGroupViewSet, basename="core_todo_group")
router.register(r"todos", CoreTodoViewSet, basename="core_todo")

urlpatterns = [
    # Authentication
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="register"),
    # User profile
    path("me/", UserProfileView.as_view(), name="user_profile"),
    # Email verification
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "auth/resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
    # Password management
    path(
        "auth/forgot-password/",
        RequestResetPasswordView.as_view(),
        name="request_reset_password",
    ),
    path(
        "auth/reset-password/",
        ResetPasswordView.as_view(),
        name="reset_password",
    ),
    path(
        "auth/change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
    # API routes
    path("", include(router.urls)),
]
