from django.contrib import admin

from .models import Todo, TodoGroup


@admin.register(TodoGroup)
class TodoGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "todos_count", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at", "owner"]
    search_fields = ["name", "description", "owner__username", "owner__email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]

    def todos_count(self, obj):
        return obj.todos.count()

    todos_count.short_description = "Todos Count"


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ["title", "group", "is_completed", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at", "is_completed", "group"]
    search_fields = ["title", "description", "group__name"]
    ordering = ["-created_at"]
