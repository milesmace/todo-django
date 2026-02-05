from config.accessor import config
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.service.auth_email_service import AuthEmailService
from core.service.token_service import (
    TokenExpiredError,
    TokenInvalidError,
    TokenService,
)

User = get_user_model()


class UserAuthService:
    """Service for user authentication operations."""

    @classmethod
    def request_email_verification(cls, email: str) -> None:
        """Request an email verification email for a user."""

        user = User.objects.get(email=email)

        token = TokenService.generate_email_verification_token(user)

        frontend_url = config.get("core.app.react_app_url")
        verify_url = f"{frontend_url}/auth/verify-email?token={token}"

        AuthEmailService.send_verification_email(email, verify_url)

    @classmethod
    def verify_email(cls, email: str, token: str) -> bool:
        """Verify a user's email address using a token."""

        user = TokenService.verify_email_verification_token(token)
        if user.email != email:
            return False

        security = user.get_security_metadata()
        if security.get("email_verified"):
            return False

        security["email_verified"] = True
        security["email_verified_at"] = timezone.now().isoformat()

        user.set_security_metadata(**security)

        return True

    @classmethod
    def request_password_reset(cls, email: str) -> None:
        """Request a password reset email for a user."""

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        token = TokenService.generate_password_reset_token(user)

        frontend_url_template = config.get("core.app.react_app_url")
        reset_url = f"{frontend_url_template}/reset-password?token={token}"

        AuthEmailService.send_password_reset_email(email, reset_url)

    @classmethod
    def reset_password(cls, email: str, token: str, new_password: str) -> bool:
        """Reset a user's password using a token."""

        try:
            user = TokenService.verify_password_reset_token(token)
        except TokenExpiredError:
            return False
        except TokenInvalidError:
            return False

        user.set_password(new_password)
        security = user.get_security_metadata()
        security["password_changed_at"] = timezone.now().isoformat()
        user.set_security_metadata(**security)

        user.save()
        return True
