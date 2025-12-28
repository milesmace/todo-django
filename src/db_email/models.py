from collections.abc import Sequence
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models


class EmailTemplate(models.Model):
    """
    A model to store email templates.
    """

    identifier = models.CharField(max_length=255, unique=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Create a Default Template Version for the newly created template
        _default_template_version = EmailTemplateVersion.objects.create(
            template=self,
            version="v1",
            is_active=True,
            subject="Default Subject",
            body="Default Body",
        )

    def __str__(self) -> str:
        return f"{self.identifier}"

    class Meta:
        ordering: Sequence[str] = ["-created_at"]
        verbose_name: str = "Email Template"
        verbose_name_plural: str = "Email Templates"


class EmailTemplateVersion(models.Model):
    """
    A model to store email template versions.
    """

    version = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False, db_index=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            original = EmailTemplateVersion.objects.get(pk=self.pk)
            if original.template != self.template:
                raise ValidationError(
                    "Template of a TemplateVersion cannot be modified after creating"
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.template.identifier} {self.version}"

    class Meta:
        # Constraints
        constraints: ClassVar[Sequence[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["template", "version"],
                name="unique_template_version",
            ),
            models.UniqueConstraint(
                fields=["template"],
                condition=models.Q(is_active=True),
                name="unique_active_version_per_template",
            ),
        ]

        ordering: Sequence[str] = ["-created_at"]
        verbose_name: str = "Email Template Version"
        verbose_name_plural: str = "Email Template Versions"


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
