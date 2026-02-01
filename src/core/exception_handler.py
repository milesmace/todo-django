"""
Custom exception handler for DRF that formats exceptions with a 'code' field
for better error handling in the React frontend.
"""

from rest_framework.views import exception_handler

from .exceptions import EmailNotVerifiedException


def custom_exception_handler(exc, context):
    """
    Custom exception handler that adds a 'code' field to error responses.

    This allows the React app to programmatically identify specific error types
    (like email_not_verified) and show appropriate UI (like a resend verification button).
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Check if this is our custom EmailNotVerifiedException
        if isinstance(exc, EmailNotVerifiedException):
            # Format the response to match the pattern used in VerifyEmailView
            response.data = {
                "error": "Email not verified",
                "message": str(exc.detail),
                "code": exc.default_code,
            }
        elif hasattr(exc, "default_code") and exc.default_code:
            # For other APIExceptions with a code, include it in the response
            if isinstance(response.data, dict):
                response.data["code"] = exc.default_code

    return response
