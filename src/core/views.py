from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from todo.models import Todo, TodoGroup
from todo.views import TodoGroupViewSet, TodoViewSet
from todoapp.settings import APP_CONFIG

from .permissions import IsAppUserGroupMember
from .serializers import (
    ResendVerificationEmailSerializer,
    UserRegistrationSerializer,
    VerifyEmailSerializer,
)
from .service.token_service import (
    EmailMismatchError,
    TokenExpiredError,
    TokenInvalidError,
    TokenService,
)
from .service.user_auth_service import UserAuthService

User = get_user_model()


class CoreTodoGroupViewSet(TodoGroupViewSet):
    def get_permissions(self):
        return [IsAppUserGroupMember()] + list(super().get_permissions())


class CoreTodoViewSet(TodoViewSet):
    def get_permissions(self):
        return [IsAppUserGroupMember()] + list(super().get_permissions())


class RegisterView(APIView):
    """
    Register a new user account.

    After registration, a verification email is sent to the user's email address.
    The user can login immediately but some features may be restricted until
    email is verified.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Assign user to App Users group
            group_name = APP_CONFIG["APP_USERS_GROUP_NAME"]
            group = Group.objects.get(name=group_name)
            user.groups.add(group)

            UserAuthService.request_email_verification(user.email)

            # Create default todo group for the user
            todo_group = TodoGroup.objects.create(
                name="Work 💼",
                owner=user,
            )

            # Create 3 sample todos for that todo group
            Todo.objects.create(
                title="Plan the next weeks schedule",
                group=todo_group,
            )
            Todo.objects.create(
                title="Connect with client regarding project",
                group=todo_group,
            )
            Todo.objects.create(
                title="Email the report of work log to the client",
                group=todo_group,
            )

            return Response(
                {
                    "message": "User registered successfully. Please check your email to verify your account.",
                    "email": user.email,
                    "name": user.name,
                    "email_verified": False,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    Verify a user's email address using a token.

    The token is sent to the user's email address during registration
    or when they request a new verification email.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]

        try:
            user = TokenService.verify_email_verification_token(token)
        except TokenExpiredError:
            return Response(
                {
                    "error": "Token expired",
                    "message": "The verification link has expired. Please request a new verification email.",
                    "code": "token_expired",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EmailMismatchError:
            return Response(
                {
                    "error": "Email changed",
                    "message": "Your email address has changed since this verification was requested. Please request a new verification email.",
                    "code": "email_mismatch",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TokenInvalidError:
            return Response(
                {
                    "error": "Invalid token",
                    "message": "The verification link is invalid.",
                    "code": "token_invalid",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if already verified (idempotent)
        security = user.get_security_metadata()
        if security.get("email_verified"):
            return Response(
                {
                    "message": "Email already verified.",
                    "email": user.email,
                    "email_verified": True,
                    "email_verified_at": security.get("email_verified_at"),
                },
                status=status.HTTP_200_OK,
            )

        # Mark email as verified
        user.set_security_metadata(
            email_verified=True,
            email_verified_at=timezone.now().isoformat(),
        )

        return Response(
            {
                "message": "Email verified successfully.",
                "email": user.email,
                "email_verified": True,
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationEmailView(APIView):
    """
    Resend verification email to a user.

    Rate limited to prevent abuse.
    """

    permission_classes = [AllowAny]
    throttle_scope = "resend_verification"

    def post(self, request: Request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        # Generic success response (don't reveal if email exists)
        success_response = Response(
            {
                "message": "If an account exists with this email and is not yet verified, a verification email has been sent.",
            },
            status=status.HTTP_200_OK,
        )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "error": "User not found",
                    "message": "No user found with this email.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if already verified
        security = user.get_security_metadata()
        if security.get("email_verified"):
            return Response(
                {
                    "error": "Email already verified",
                    "message": "The email is already verified.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Send verification email
        UserAuthService.request_email_verification(email)

        return success_response


class RequestResetPasswordView(APIView):
    """
    Request a password reset email.

    Sends a password reset link to the user's email if the account exists.
    Always returns success to prevent email enumeration.
    """

    permission_classes = [AllowAny]
    throttle_scope = "password_reset"

    def post(self, request: Request):
        email = request.data.get("email", None)

        if not email:
            return Response(
                {
                    "error": "Validation Error",
                    "details": {"email": "Email is required"},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        UserAuthService.request_password_reset(email)

        return Response(
            {
                "message": "If an account exists with this email, a password reset link has been sent.",
            },
            status=status.HTTP_200_OK,
        )
