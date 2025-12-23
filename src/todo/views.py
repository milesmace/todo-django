from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter

from .models import Todo, TodoGroup
from .serializers import TodoGroupSerializer, TodoSerializer


class TodoGroupViewSet(viewsets.ModelViewSet):
    serializer_class = TodoGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TodoGroup.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data["owner"] != self.request.user:
            raise PermissionDenied(
                "You can only update todos in your own groups.",
            )
        serializer.save()

    def perform_destroy(self, instance: TodoGroup):
        if instance.owner != self.request.user:
            raise PermissionDenied(
                "You can only delete todos in your own groups.",
            )
        instance.delete()


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]

    def get_queryset(self):
        # Only return todos that belong to groups owned by the current user
        user_groups = TodoGroup.objects.filter(owner=self.request.user)
        return Todo.objects.filter(group__in=user_groups, is_completed=False)

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
        group = serializer.validated_data.get("group")
        # Validate that the group belongs to the current user
        if group.owner != self.request.user:
            raise PermissionDenied(
                "You can only move todos to your own groups.",
                status.HTTP_403_FORBIDDEN,
            )
        serializer.save()

    def perform_destroy(self, instance: Todo):
        if instance.group.owner != self.request.user:
            raise PermissionDenied(
                "You can only delete todos in your own groups.",
            )
        instance.delete()
