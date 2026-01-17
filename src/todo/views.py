from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from .models import Todo, TodoGroup
from .serializers import TodoGroupSerializer, TodoSerializer


class TodoGroupViewSet(viewsets.ModelViewSet):
    serializer_class = TodoGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return TodoGroup.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        if (
            serializer.validated_data.get("owner")
            and serializer.validated_data["owner"] != self.request.user
        ):
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
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_completed", "group"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "is_completed", "created_at", "updated_at"]
    ordering = ["-created_at"]

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
        group = serializer.validated_data.get("group")
        # Validate that the group belongs to the current user (if group is being changed)
        if group and group.owner != self.request.user:
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

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Toggle the is_completed status of a todo."""
        todo = self.get_object()
        todo.is_completed = not todo.is_completed
        todo.save(update_fields=["is_completed", "updated_at"])
        serializer = self.get_serializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)
