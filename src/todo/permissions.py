from rest_framework.permissions import BasePermission
from todoapp.settings import APP_CONFIG


class IsAppUserGroupMember(BasePermission):
    """
    Custom permission to only allow members of a common group to access the object.
    Assumes the model instance has a 'group' attribute with a 'members' ManyToMany field.
    """

    def has_permission(self, request, view):
        app_user_group_name = APP_CONFIG["APP_USERS_GROUP_NAME"]
        if request.user.groups.filter(name=app_user_group_name).exists():
            return True
