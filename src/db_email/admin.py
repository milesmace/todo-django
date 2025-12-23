from django.contrib import admin

from .models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["identifier", "subject", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["identifier", "subject"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
