from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token

from .models import User


class JWTAuthenticationWithTimezone(JWTAuthentication):
    def authenticate(self, request: Request) -> tuple[User, Token] | None:
        result = super().authenticate(request)

        if result:
            user, _token = result
            if user.timezone:
                try:
                    timezone.activate(ZoneInfo(user.timezone))
                except Exception:
                    timezone.activate(ZoneInfo("UTC"))

        return result
