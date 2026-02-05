from django.contrib import admin

from .models import Todo, TodoGroup


@admin.register(TodoGroup)
class TodoGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "todos_count", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at", "owner"]
    search_fields = ["name", "description", "owner__email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]

    def todos_count(self, obj):
        return obj.todos.count()

    todos_count.short_description = "Todos Count"


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "group_owner",
        "group",
        "is_completed",
        "due_date",
        "created_at",
        "updated_at",
    ]
    list_filter = ["created_at", "updated_at", "is_completed", "group", "group__owner"]
    search_fields = ["title", "description", "group__name"]
    ordering = ["-created_at"]

    def group_owner(self, obj):
        return obj.group.owner

    group_owner.short_description = "Group Owner"
