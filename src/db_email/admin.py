from django.contrib import admin

from .models import EmailTemplate, EmailTemplateVersion


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["identifier", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["identifier"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(EmailTemplateVersion)
class EmailTemplateVersionAdmin(admin.ModelAdmin):
    list_display = ["template", "version", "subject", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["template", "subject", "body"]
    sortable_by = ["template", "version", "created_at", "updated_at"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
