"""
Authentication email service.

Handles sending authentication-related emails such as email verification
and password reset.
"""

from config.accessor import config
from db_email.services import TemplateService
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


class AuthEmailService:
    """Service for sending authentication-related emails."""

    @staticmethod
    def _get_from_email() -> str:
        """Get the default from email from config."""
        return config.get("core.email.default_from_email", "noreply@example.com")

    @classmethod
    def send_verification_email(cls, email: str, verification_url: str) -> None:
        """
        Send email verification email to a user.

        Args:
            email: The email to send verification email
            verification_url: The URL to verify the email
        """

        user = User.objects.get(email=email)

        context = {
            "email": email,
            "name": user.name,
            "verification_url": verification_url,
        }
        content = TemplateService.get_template("email_verification", context)

        send_mail(
            subject=content.subject,
            message=content.body,
            html_message=content.body,
            from_email=cls._get_from_email(),
            recipient_list=[email],
            fail_silently=False,
        )

    @classmethod
    def send_password_reset_email(cls, email: str, reset_url: str) -> None:
        """
        Send password reset email to a user.

        Args:
            email: The email to send password reset email to
            reset_url: The URL to reset the password
        """
        context = {
            "email": email,
            "reset_url": reset_url,
        }

        content = TemplateService.get_template("password_reset", context)

        send_mail(
            subject=content.subject,
            message=content.body,
            html_message=content.body,
            from_email=cls._get_from_email(),
            recipient_list=[email],
            fail_silently=False,
        )
