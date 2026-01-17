"""
Dynamic CORS configuration using django-cors-headers signals.

This module provides dynamic CORS origin validation by reading allowed origins
from the application's configuration system instead of static Django settings.

The signal is connected when the core app is ready (see apps.py).
"""

from config.accessor import config
from corsheaders.signals import check_request_enabled


def cors_allow_origin(sender, request, **kwargs):
    """
    Dynamically check if the request origin should be allowed for CORS.

    This signal handler is called for each request that includes an Origin header.
    It checks the origin against the list of allowed origins stored in the
    application configuration.

    Args:
        sender: The sender of the signal (CorsMiddleware)
        request: The Django request object
        **kwargs: Additional keyword arguments

    Returns:
        bool: True if the origin is allowed, False otherwise
    """
    origin = request.META.get("HTTP_ORIGIN", "")

    if not origin:
        return False

    # Get allowed origins from config (comma-separated string)
    allowed_origins_str = config.get("core.cors.allowed_origins", "")

    if not allowed_origins_str:
        return False

    # Parse comma-separated origins and check if request origin is allowed
    allowed_origins = [o.strip() for o in allowed_origins_str.split(",") if o.strip()]

    return origin in allowed_origins


def connect_cors_signal():
    """Connect the CORS signal handler."""
    check_request_enabled.connect(cors_allow_origin)
