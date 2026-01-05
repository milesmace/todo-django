"""
Configurable SMTP Email Backend

This email backend extends Django's SMTP backend to read configuration
from the app's config system instead of Django settings. This allows
email configuration to be changed at runtime via the admin interface.
"""

from config.accessor import config
from django.core.mail.backends.smtp import EmailBackend as DjangoEmailBackend


class ConfigurableEmailBackend(DjangoEmailBackend):
    """
    An SMTP email backend that reads configuration from the config system.

    This backend inherits from Django's EmailBackend without any modifications
    to the email sending logic. It only overrides the initialization to fetch
    configuration values from the database via the config accessor.

    Configuration is read from: core.email.*
        - email_host: SMTP server hostname
        - email_port: SMTP server port
        - email_host_user: Username for SMTP authentication
        - email_host_password: Password for SMTP authentication
        - email_use_tls: Whether to use TLS (STARTTLS)
        - email_use_ssl: Whether to use SSL
        - email_timeout: Connection timeout in seconds
    """

    def __init__(
        self,
        host=None,
        port=None,
        username=None,
        password=None,
        use_tls=None,
        use_ssl=None,
        timeout=None,
        ssl_keyfile=None,
        ssl_certfile=None,
        fail_silently=False,
        **kwargs,
    ):
        """
        Initialize the email backend with configuration from the config system.

        Parameters passed directly to this constructor will override
        the values from the config system.
        """
        # Fetch configuration from the config system
        config_host = config.get("core.email.email_host", "localhost")
        config_port = config.get("core.email.email_port", 587)
        config_username = config.get("core.email.email_host_user", "")
        config_password = config.get("core.email.email_host_password", "")
        config_use_tls = config.get("core.email.email_use_tls", True)
        config_use_ssl = config.get("core.email.email_use_ssl", False)
        config_timeout = config.get("core.email.email_timeout", 30)

        # Use passed values if provided, otherwise use config values
        super().__init__(
            host=host if host is not None else config_host,
            port=port if port is not None else config_port,
            username=username if username is not None else config_username,
            password=password if password is not None else config_password,
            use_tls=use_tls if use_tls is not None else config_use_tls,
            use_ssl=use_ssl if use_ssl is not None else config_use_ssl,
            timeout=timeout if timeout is not None else config_timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            fail_silently=fail_silently,
            **kwargs,
        )
