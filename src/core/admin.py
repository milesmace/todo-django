from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""

    # Fields to display in list view
    list_display = [
        "email",
        "name",
        "is_staff",
        "is_active",
        "is_superuser",
        "timezone",
        "created_at",
    ]

    # Filters in the right sidebar
    list_filter = [
        "is_staff",
        "is_active",
        "is_superuser",
        "created_at",
        "timezone",
    ]

    # Searchable fields
    search_fields = ["email", "name"]

    # Default ordering
    ordering = ["-created_at"]

    # Fields shown when editing a user
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name", "timezone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Metadata", {"fields": ("metadata",)}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    # Fields shown when creating a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "name", "timezone"),
            },
        ),
    )

    # Read-only fields
    readonly_fields = ["created_at", "updated_at", "last_login"]

    # Fields to show in the detail view
    filter_horizontal = ["groups", "user_permissions"]
