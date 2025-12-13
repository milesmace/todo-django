from django.contrib import admin

from .models import ConfigValue


@admin.register(ConfigValue)
class ConfigValueAdmin(admin.ModelAdmin):
    """Basic admin for ConfigValue model - mainly for debugging purposes."""

    list_display = ("app_label", "path", "value")
    list_filter = ("app_label",)
    search_fields = ("app_label", "path", "value")
    ordering = ("app_label", "path")
