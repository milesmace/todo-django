"""
Token service for generating and verifying signed tokens.

Uses Django's signing module for stateless, cryptographically secure tokens.
"""

from config.accessor import config
from django.contrib.auth import get_user_model
from django.core import signing

User = get_user_model()


class TokenError(Exception):
    """Base exception for token errors."""

    pass


class TokenExpiredError(TokenError):
    """Token has expired."""

    pass


class TokenInvalidError(TokenError):
    """Token is invalid or tampered with."""

    pass


class EmailMismatchError(TokenError):
    """Email in token doesn't match user's current email."""

    pass


class TokenService:
    """Service for generating and verifying signed tokens."""

    # Salt values for different token types (prevents token reuse across purposes)
    SALT_EMAIL_VERIFICATION = "email-verification"
    SALT_PASSWORD_RESET = "password-reset"

    PURPOSE_EMAIL_VERIFICATION = "email_verification"
    PURPOSE_PASSWORD_RESET = "password_reset"

    @staticmethod
    def _get_verification_expiry_seconds() -> int:
        """Get token expiry in seconds from config."""
        seconds = config.get("core.auth.verification_token_expiry", 7200)
        return seconds

    @staticmethod
    def _get_password_reset_expiry_seconds() -> int:
        """Get token expiry in seconds from config."""
        seconds = config.get("core.auth.password_reset_token_expiry", 300)
        return seconds

    @classmethod
    def generate_email_verification_token(cls, user: User) -> str:
        """
        Generate a signed token for email verification.

        Args:
            user: The user to generate token for

        Returns:
            str: The signed token
        """
        payload = {
            "user_id": user.id,
            "email": user.email,
            "purpose": cls.PURPOSE_EMAIL_VERIFICATION,
        }
        return signing.dumps(payload, salt=cls.SALT_EMAIL_VERIFICATION)

    @classmethod
    def verify_email_verification_token(cls, token: str) -> User:
        """
        Verify an email verification token and return the user.

        Args:
            token: The signed token to verify

        Returns:
            User: The user associated with the token

        Raises:
            TokenExpiredError: If the token has expired
            TokenInvalidError: If the token is invalid
            EmailMismatchError: If the email has changed since token was issued
        """
        max_age = cls._get_verification_expiry_seconds()

        try:
            payload = signing.loads(
                token,
                salt=cls.SALT_EMAIL_VERIFICATION,
                max_age=max_age,
            )
        except signing.SignatureExpired:
            raise TokenExpiredError("Verification token has expired") from None
        except signing.BadSignature:
            raise TokenInvalidError("Invalid verification token") from None

        # Validate payload structure
        if not isinstance(payload, dict) or "user_id" not in payload:
            raise TokenInvalidError("Invalid token payload")

        # Get the user
        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise TokenInvalidError("User not found") from None

        # Verify email hasn't changed since token was issued
        if payload.get("email") != user.email:
            raise EmailMismatchError(
                "Email address has changed since verification was requested"
            )

        if payload.get("purpose") != cls.PURPOSE_EMAIL_VERIFICATION:
            raise TokenInvalidError("Invalid token")

        return user

    @classmethod
    def generate_password_reset_token(cls, user: User) -> str:
        """
        Generate a signed token for password reset.

        Args:
            user: The user to generate token for

        Returns:
            str: The signed token
        """
        payload = {
            "user_id": user.id,
            "email": user.email,
            "purpose": cls.PURPOSE_PASSWORD_RESET,
        }
        return signing.dumps(payload, salt=cls.SALT_PASSWORD_RESET)

    @classmethod
    def verify_password_reset_token(cls, token: str) -> User:
        """
        Verify a password reset token and return the user.

        Args:
            token: The signed token to verify

        Returns:
            User: The user associated with the token

        Raises:
            TokenExpiredError: If the token has expired
            TokenInvalidError: If the token is invalid
        """
        max_age = cls._get_password_reset_expiry_seconds()

        try:
            payload = signing.loads(
                token,
                salt=cls.SALT_PASSWORD_RESET,
                max_age=max_age,
            )
        except signing.SignatureExpired:
            raise TokenExpiredError("Password reset token has expired") from None
        except signing.BadSignature:
            raise TokenInvalidError("Invalid password reset token") from None

        # Validate payload structure
        if not isinstance(payload, dict) or "user_id" not in payload:
            raise TokenInvalidError("Invalid token payload")

        # Get the user
        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            raise TokenInvalidError("User not found") from None

        if payload.get("purpose") != cls.PURPOSE_PASSWORD_RESET:
            raise TokenInvalidError("Invalid token")

        return user
