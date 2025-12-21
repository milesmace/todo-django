from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Todo, TodoGroup
from .permissions import IsAppUserGroupMember
from .serializers import TodoGroupSerializer, TodoSerializer


class TodoGroupViewSet(viewsets.ModelViewSet):
    serializer_class = TodoGroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppUserGroupMember]

    def get_queryset(self):
        return TodoGroup.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppUserGroupMember]

    def get_queryset(self):
        # Only return todos that belong to groups owned by the current user
        user_groups = TodoGroup.objects.filter(owner=self.request.user)
        return Todo.objects.filter(group__in=user_groups)

    def perform_create(self, serializer):
        group = serializer.validated_data.get("group")
        # Validate that the group belongs to the current user
        if group.owner != self.request.user:
            raise PermissionDenied(
                "You can only create todos in your own groups.",
                status.HTTP_403_FORBIDDEN,
            )
        serializer.save()

    def perform_update(self, serializer):
        group = serializer.validated_data.get("group", serializer.instance.group)
        # Validate that the group belongs to the current user
        if group.owner != self.request.user:
            raise PermissionDenied(
                "You can only move todos to your own groups.",
                status.HTTP_403_FORBIDDEN,
            )
        serializer.save()
