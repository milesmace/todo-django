from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from todo.views import TodoGroupViewSet, TodoViewSet
from todoapp.settings import APP_CONFIG

from .permissions import IsAppUserGroupMember
from .serializers import UserRegistrationSerializer

User = get_user_model()


class CoreTodoGroupViewSet(TodoGroupViewSet):
    def get_permissions(self):
        return [IsAppUserGroupMember()] + list(super().get_permissions())


class CoreTodoViewSet(TodoViewSet):
    def get_permissions(self):
        return [IsAppUserGroupMember()] + list(super().get_permissions())


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Assign user to App Users group
            group_name = APP_CONFIG["APP_USERS_GROUP_NAME"]
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass  # Group doesn't exist yet, skip assignment

            return Response(
                {
                    "message": "User registered successfully.",
                    "email": user.email,
                    "name": user.name,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

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

        def send_success_response():
            return Response(
                {
                    "message": "If an account exists with this email, a "
                    + "reset password link is sent to your email",
                },
                status=status.HTTP_200_OK,
            )

        # fetch the user with this email
        try:
            _user = User.objects.get(email=email)
        except User.DoesNotExist:
            return send_success_response()

        # TODO: Send an email to that user
        # Send an email to that user
