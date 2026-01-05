from django.db import models


class EmailLogMessage(models.Model):
    """
    Stores the email log details including subject, body, and sender.
    Each message can have multiple recipients tracked via EmailLog.
    """

    subject = models.CharField(max_length=255)
    body = models.TextField()
    from_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Log Message"
        verbose_name_plural = "Email Log Messages"

    def __str__(self):
        return f"{self.subject} ({self.from_email})"


class EmailLog(models.Model):
    """
    Represents a single email delivery to one recipient.
    Tracks the delivery status, retry count, and any errors.
    """

    class RecipientType(models.TextChoices):
        TO = "to", "To"
        CC = "cc", "Cc"
        BCC = "bcc", "Bcc"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    email_log_message = models.ForeignKey(
        EmailLogMessage,
        on_delete=models.CASCADE,
        related_name="email_logs",
    )
    to_email = models.EmailField()
    recipient_type = models.CharField(max_length=5, choices=RecipientType.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    retry_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"

    def __str__(self):
        return f"{self.to_email} ({self.status})"
