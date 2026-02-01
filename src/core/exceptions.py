"""
Custom exceptions for the core app.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


class EmailNotVerifiedException(APIException):
    """
    Exception raised when a user tries to access a resource but their email is not verified.

    This exception includes a 'code' field that the React app can check to determine
    if it should show a resend verification email button.
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You need to verify your email before you can use the app."
    default_code = "email_not_verified"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        super().__init__(detail, code)
