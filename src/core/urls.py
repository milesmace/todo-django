from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CoreTodoGroupViewSet,
    CoreTodoViewSet,
    RegisterView,
    RequestResetPasswordView,
    ResendVerificationEmailView,
    VerifyEmailView,
)

router = DefaultRouter()
router.register(r"groups", CoreTodoGroupViewSet, basename="core_todo_group")
router.register(r"todos", CoreTodoViewSet, basename="core_todo")

urlpatterns = [
    # Authentication
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    # Email verification
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "auth/resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
    # Password reset
    path(
        "auth/forgot-password/",
        RequestResetPasswordView.as_view(),
        name="request_reset_password",
    ),
    # API routes
    path("", include(router.urls)),
]
