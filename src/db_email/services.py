"""
Service layer for email template operations.

This module provides business logic for fetching and working with
email templates stored in the database.
"""

from dataclasses import dataclass

from django.template import engines

from .models import EmailTemplate, EmailTemplateVersion


class TemplateNotFoundError(Exception):
    """Raised when a template with the given identifier doesn't exist."""

    pass


class ActiveTemplateVersionNotFoundError(Exception):
    """Raised when no active version exists for the given template."""

    pass


@dataclass
class TemplateContent:
    """
    Data class representing the content of an email template.

    Attributes:
        subject: The email subject line
        body: The email body content
    """

    subject: str
    body: str


class TemplateService:
    """
    Service for working with email templates.
    """

    @classmethod
    def get_template(cls, identifier: str, context: dict = None) -> TemplateContent:
        """
        Fetch the subject and body from the active version of a template.

        This function retrieves the email template by its identifier and returns
        the subject and body from its currently active version.

        Args:
            identifier: The unique identifier of the email template

        Returns:
            TemplateContent: A dataclass containing the subject and body

        Raises:
            TemplateNotFoundError: If no template exists with the given identifier
            ActiveTemplateVersionNotFoundError: If the template has no active version
        """

        try:
            template = EmailTemplate.objects.get(identifier=identifier)
        except EmailTemplate.DoesNotExist:
            raise TemplateNotFoundError(
                f"Template with identifier '{identifier}' not found"
            ) from None

        active_version = EmailTemplateVersion.objects.filter(
            template=template,
            is_active=True,
        ).first()

        if not active_version:
            raise ActiveTemplateVersionNotFoundError(
                f"No active version found for template '{identifier}'"
            )

        template = engines["db_email"].from_string(active_version.body)

        if context and len(context) > 0:
            body = template.render(context)
        else:
            body = template.render()

        return TemplateContent(
            subject=active_version.subject,
            body=body,
        )
