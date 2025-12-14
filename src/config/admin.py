from django.contrib import admin

from .models import ConfigValue


@admin.register(ConfigValue)
class ConfigValueAdmin(admin.ModelAdmin):
    """Basic admin for ConfigValue model - mainly for debugging purposes."""

    list_display = ("app_label", "path", "value_preview")
    list_filter = ("app_label",)
    search_fields = ("app_label", "path", "value")
    ordering = ("app_label", "path")
    readonly_fields = ("app_label", "path", "value_preview")

    def value_preview(self, obj):
        """Show value preview, masking secrets."""
        if not obj.value:
            return "(empty)"
        # Mask potentially encrypted/secret values (they start with 'gAAAAA' for Fernet)
        if obj.value.startswith("gAAAAA") or len(obj.value) > 50:
            return "*** (encrypted/secret value hidden) ***"
        # Truncate long values
        if len(obj.value) > 100:
            return obj.value[:100] + "..."
        return obj.value

    value_preview.short_description = "Value"
