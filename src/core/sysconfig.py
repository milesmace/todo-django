"""
System Configuration for Core App

This file defines the configuration options for the Core application.
"""

from config.frontend_models import (
    BooleanFrontendModel,
    IntegerFrontendModel,
    SecretFrontendModel,
    StringFrontendModel,
)
from config.registry import Field, Section, register_config
from config.validators import PortValidator, Required, UrlValidator


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
            validators=[Required(), UrlValidator()],
        )

    class Email(Section):
        """Email settings."""

        label: str = "Email Settings"
        sort_order: int = 20

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
            comment="Whether to use TLS (STARTTLS) for the connection. Typically used with port 587.",
            default=True,
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
