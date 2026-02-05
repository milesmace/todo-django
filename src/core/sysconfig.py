"""
System Configuration for Core App

This file defines the configuration options for the Core application.
"""

from config.frontend_models import (
    BooleanFrontendModel,
    IntegerFrontendModel,
    SecretFrontendModel,
    StringFrontendModel,
    TextareaFrontendModel,
)
from config.registry import Field, Section, register_config
from config.validators import (
    EmailValidator,
    PortValidator,
    RangeValidator,
    Required,
    UrlValidator,
)
from todoapp.settings import DEBUG


@register_config("core")
class CoreSysConfig:
    """Configuration definition for the Core app."""

    class App(Section):
        """Todo App Configuration."""

        label: str = "App Configuration"
        sort_order: int = 10

        react_app_url: Field = Field(
            StringFrontendModel,
            label="React App URL",
            placeholder="https://example.com",
            sort_order=10,
            validators=[
                Required(),
                UrlValidator(schemes=["https"] if not DEBUG else ["http", "https"]),
            ],
        )

        contact_email = Field(
            StringFrontendModel,
            label="Contact Email",
            placeholder="support@example.com",
            sort_order=20,
            validators=[EmailValidator()],
        )

    class Cors(Section):
        """CORS settings for frontend applications."""

        label: str = "CORS Settings"
        sort_order: int = 15

        allowed_origins = Field(
            TextareaFrontendModel,
            label="Allowed Origins",
            comment="Comma-separated list of allowed origins for CORS requests. Example: http://localhost:3000, https://app.example.com",
            default="http://localhost:3000",
            placeholder="http://localhost:3000, https://app.example.com",
            sort_order=10,
        )

    class Auth(Section):
        """Authentication settings."""

        label: str = "Authentication Settings"
        sort_order: int = 20

        verification_token_expiry = Field(
            IntegerFrontendModel,
            label="Verification Token Expiry (seconds)",
            comment="How long email verification tokens remain valid. Provide a value between 300 and 604800 seconds (5 minutes and 1 week).",
            default=86_400,  # 24 hours
            sort_order=10,
            validators=[RangeValidator(300, 604800)],
        )

        password_reset_token_expiry = Field(
            IntegerFrontendModel,
            label="Password Reset Token Expiry (seconds)",
            comment="How long password reset tokens remain valid. Provide a value between 60 and 86400 seconds (1 minute and 1 day).",
            default=600,  # 10 minutes
            sort_order=15,
            validators=[RangeValidator(60, 86400)],
        )

        refresh_token_cookie_expiry = Field(
            IntegerFrontendModel,
            label="Refresh Token Cookie Expiry (seconds)",
            comment="How long refresh tokens remain valid. Provide a value between 3600 and 604800 seconds (1 hour and 1 week).",
            default=86_400,  # 1 day
            sort_order=20,
            validators=[RangeValidator(3_600, 604_800)],
        )

    class Email(Section):
        """Email settings."""

        label: str = "Email Settings"
        sort_order: int = 30

        email_host = Field(
            StringFrontendModel,
            label="Email Host",
            comment="The host of your email server (e.g., smtp.gmail.com).",
            default="localhost",
            sort_order=5,
            validators=[Required()],
        )

        email_port = Field(
            IntegerFrontendModel,
            label="Email Port",
            comment="The port of your email server (e.g., 587 for TLS, 465 for SSL).",
            default=587,
            sort_order=10,
            validators=[Required(), PortValidator()],
        )

        email_host_user = Field(
            StringFrontendModel,
            label="Email Username",
            comment="The username for authenticating with the email server.",
            default="",
            sort_order=15,
        )

        email_host_password = Field(
            SecretFrontendModel,
            label="Email Password",
            comment="The password for authenticating with the email server.",
            default="",
            sort_order=20,
        )

        email_use_tls = Field(
            BooleanFrontendModel,
            label="Use TLS",
            comment="Whether to use TLS (STARTTLS) for the connection. Typically used with port 587. Set to False for development mail servers like MailCatcher.",
            default=False,
            sort_order=25,
        )

        email_use_ssl = Field(
            BooleanFrontendModel,
            label="Use SSL",
            comment="Whether to use SSL for the connection. Typically used with port 465. Cannot be used with TLS.",
            default=False,
            sort_order=30,
        )

        email_timeout = Field(
            IntegerFrontendModel,
            label="Timeout (seconds)",
            comment="Connection timeout in seconds. Leave empty to use the default.",
            default=30,
            sort_order=35,
        )

        default_from_email = Field(
            StringFrontendModel,
            label="Default From Email",
            comment="The default 'From' email address for outgoing emails.",
            default="noreply@example.com",
            sort_order=40,
            validators=[Required()],
        )
