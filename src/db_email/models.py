from django.db import models


class EmailTemplate(models.Model):
    """
    A model to store email templates.
    """

    identifier = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.identifier

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
