from rest_framework import serializers

from .models import Todo, TodoGroup


class TodoGroupSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    todos_count = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    class Meta:
        model = TodoGroup
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "todos_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "created_at", "updated_at"]

    def get_todos_count(self, obj):
        return obj.todos.count()


class TodoSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=TodoGroup.objects.all())
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Todo
        fields = [
            "id",
            "title",
            "description",
            "is_completed",
            "group",
            "group_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
