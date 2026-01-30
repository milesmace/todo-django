from config.accessor import config
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView as BaseTokenRefreshView,
)
from todo.models import Todo, TodoGroup
from todo.views import TodoGroupViewSet, TodoViewSet
from todoapp.settings import APP_CONFIG

from .permissions import IsAppUserGroupMember
from .serializers import (
    ChangePasswordSerializer,
    ResendVerificationEmailSerializer,
    ResetPasswordSerializer,
    UserProfileSerializer,
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


class LoginView(TokenObtainPairView):
    """
    Login a user and return a JWT token.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request):
        response: Response = super().post(request)

        refresh_token = response.data.pop("refresh")

        response.set_cookie(
            "refresh_token",
            str(refresh_token),
            httponly=True,
            secure=True,
            samesite="None",
            path="/api/auth/",
            max_age=config.get("core.auth.refresh_token_cookie_expiry"),
        )

        return response


class TokenRefreshView(BaseTokenRefreshView):
    """
    Refresh a JWT token and return a new JWT token.
    """

    def post(self, request: Request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {
                    "error": "Refresh token not found",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        response = Response(
            {
                "access": serializer.validated_data["access"],
            },
            status=status.HTTP_200_OK,
        )

        return response


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


class ResetPasswordView(APIView):
    """
    Reset password using a token from the password reset email.

    Completes the forgot-password flow by setting a new password.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = TokenService.verify_password_reset_token(token)
        except TokenExpiredError:
            return Response(
                {
                    "error": "Token expired",
                    "message": "The password reset link has expired. Please request a new one.",
                    "code": "token_expired",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TokenInvalidError:
            return Response(
                {
                    "error": "Invalid token",
                    "message": "The password reset link is invalid.",
                    "code": "token_invalid",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Update security metadata
        user.set_security_metadata(password_changed_at=timezone.now().isoformat())

        return Response(
            {
                "message": "Password reset successfully. You can now login with your new password.",
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """
    Change password for authenticated users.

    Requires the current password for verification.
    """

    def post(self, request: Request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        user = request.user

        # Verify current password
        if not user.check_password(current_password):
            return Response(
                {
                    "error": "Invalid password",
                    "message": "Current password is incorrect.",
                    "code": "invalid_password",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Update security metadata
        user.set_security_metadata(password_changed_at=timezone.now().isoformat())

        return Response(
            {
                "message": "Password changed successfully.",
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(APIView):
    """
    Get or update the current user's profile.

    GET: Returns user profile information
    PATCH: Updates allowed profile fields (name, timezone)
    """

    def get(self, request: Request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
