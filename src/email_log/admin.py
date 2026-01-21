from django.contrib import admin
from django.utils.html import format_html

from .models import EmailLog, EmailLogMessage


class EmailLogInline(admin.TabularInline):
    """Inline view for email recipients within an EmailLogMessage."""

    model = EmailLog
    extra = 0
    readonly_fields = [
        "to_email",
        "recipient_type",
        "status_badge",
        "retry_count",
        "error_message",
        "created_at",
        "sent_at",
    ]
    fields = [
        "to_email",
        "recipient_type",
        "status_badge",
        "retry_count",
        "sent_at",
        "error_message",
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Status")
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "pending": "#6c757d",  # gray
            "sending": "#0d6efd",  # blue
            "sent": "#198754",  # green
            "failed": "#dc3545",  # red
            "cancelled": "#ffc107",  # yellow
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )


@admin.register(EmailLogMessage)
class EmailLogMessageAdmin(admin.ModelAdmin):
    """Admin interface for email messages."""

    list_display = [
        "subject",
        "from_email",
        "recipient_count",
        "delivery_summary",
        "created_at",
    ]
    list_filter = ["created_at", "from_email"]
    search_fields = ["subject", "from_email", "body", "email_logs__to_email"]
    ordering = ["-created_at"]
    readonly_fields = ["subject", "from_email", "body", "created_at", "body_preview"]
    inlines = [EmailLogInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("subject", "from_email")}),
        ("Content", {"fields": ("body_preview",)}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of email logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow viewing but not editing."""
        return True

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup purposes."""
        return True

    @admin.display(description="Recipients")
    def recipient_count(self, obj):
        """Display the number of recipients."""
        count = obj.email_logs.count()
        return f"{count} recipient{'s' if count != 1 else ''}"

    @admin.display(description="Delivery Status")
    def delivery_summary(self, obj):
        """Display a summary of delivery statuses."""
        logs = obj.email_logs.all()
        total = logs.count()
        if total == 0:
            return "-"

        sent = logs.filter(status="sent").count()
        failed = logs.filter(status="failed").count()
        pending = logs.filter(status__in=["pending", "sending"]).count()

        parts = []
        if sent:
            parts.append(format_html('<span style="color: #198754;">✓ {}</span>', sent))
        if failed:
            parts.append(
                format_html('<span style="color: #dc3545;">✗ {}</span>', failed)
            )
        if pending:
            parts.append(
                format_html('<span style="color: #6c757d;">⏳ {}</span>', pending)
            )

        return format_html(" / ".join([str(p) for p in parts]))

    @admin.display(description="Body Preview")
    def body_preview(self, obj):
        """Display the email body in a scrollable container."""
        return format_html(
            '<div style="max-height: 400px; overflow-y: auto; background: #f8f9fa; '
            'padding: 15px; border: 1px solid #dee2e6; border-radius: 4px;">{}</div>',
            obj.body,
        )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin interface for individual email deliveries."""

    list_display = [
        "to_email",
        "subject_preview",
        "recipient_type",
        "status_badge",
        "retry_count",
        "created_at",
        "sent_at",
    ]
    list_filter = ["status", "recipient_type", "created_at", "sent_at"]
    search_fields = [
        "to_email",
        "email_log_message__subject",
        "email_log_message__from_email",
        "error_message",
    ]
    ordering = ["-created_at"]
    readonly_fields = [
        "email_log_message",
        "to_email",
        "recipient_type",
        "status",
        "retry_count",
        "error_message",
        "created_at",
        "sent_at",
        "message_link",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Recipient",
            {"fields": ("to_email", "recipient_type", "message_link")},
        ),
        (
            "Delivery Status",
            {"fields": ("status", "retry_count", "error_message")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "sent_at")},
        ),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of email logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow viewing but not editing."""
        return True

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup purposes."""
        return True

    @admin.display(description="Subject")
    def subject_preview(self, obj):
        """Display a truncated subject from the parent message."""
        subject = obj.email_log_message.subject
        if len(subject) > 50:
            return f"{subject[:50]}..."
        return subject

    @admin.display(description="Status")
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "pending": "#6c757d",  # gray
            "sending": "#0d6efd",  # blue
            "sent": "#198754",  # green
            "failed": "#dc3545",  # red
            "cancelled": "#ffc107",  # yellow
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description="View Message")
    def message_link(self, obj):
        """Link to the parent email message."""
        from django.urls import reverse

        url = reverse(
            "admin:email_log_emaillogmessage_change",
            args=[obj.email_log_message.pk],
        )
        return format_html(
            '<a href="{}" class="button" style="padding: 5px 15px;">'
            "View Full Message</a>",
            url,
        )
