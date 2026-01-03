from django.db import models


class EmailLogMessage(models.Model):
    """
    This model stores the Email log details and the template sent
    """

    subject = models.CharField(max_length=255)
    body = models.TextField()


class EmailLogRecipient(models.Model):
    class RecipientType(models.TextChoices):
        TO = "to", "To"
        CC = "cc", "Cc"
        BSS = "bcc", "Bcc"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    email_log_message = models.ForeignKey(EmailLogMessage, on_delete=models.CASCADE)
    to_email = models.EmailField()
    recipient_type = models.CharField(max_length=5, choices=RecipientType.choices)
    status = models.CharField(max_length=20, choices=Status.choices)
    error_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
