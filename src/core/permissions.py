from rest_framework import status
from rest_framework.permissions import BasePermission
from todoapp.settings import APP_CONFIG

from .exceptions import EmailNotVerifiedException


class IsAppUserGroupMember(BasePermission):
    """
    Custom permission to only allow members of a common group to access the object.
    Assumes the model instance has a 'group' attribute with a 'members' ManyToMany field.
    """

    def has_permission(self, request, _view):
        if not request.user or not request.user.is_authenticated:
            return False

        app_user_group_name = APP_CONFIG["APP_USERS_GROUP_NAME"]
        return request.user.groups.filter(name=app_user_group_name).exists()


class IsAppUserEmailVerified(BasePermission):
    """
    Custom permission to only allow users with verified email to access the object.

    Raises a PermissionDenied exception with a 'code' field set to 'email_not_verified'
    so that the React app can detect this specific error and show a resend verification
    email button.
    """

    message = "You need to verify your email before you can use the app."
    status_code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, _view):
        if not request.user or not request.user.is_authenticated:
            return False

        app_user_group_name = APP_CONFIG["APP_USERS_GROUP_NAME"]
        if not request.user.groups.filter(name=app_user_group_name).exists():
            return True

        is_verified = request.user.get_security_metadata().get("email_verified", False)

        if not is_verified:
            # Raise a custom exception with a code that React can check for
            raise EmailNotVerifiedException()

        return True
