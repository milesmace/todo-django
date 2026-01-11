"""
Custom template loader that loads templates from the database.
"""

from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader

from .models import EmailTemplate, EmailTemplateVersion


class DBEmailTemplateLoader(BaseLoader):
    """
    A template loader that loads templates from the database.

    This loader is used by the Django template engine to resolve
    template names (e.g., in {% extends %} and {% include %}) to
    template content stored in the database.
    """

    def get_contents(self, origin):
        """
        Load template content from the database.

        Args:
            origin: The Origin object containing the template name

        Returns:
            str: The template source code

        Raises:
            TemplateDoesNotExist: If the template doesn't exist in the database
        """
        template_name = origin.name

        try:
            record = EmailTemplate.objects.get(identifier=template_name)
        except EmailTemplate.DoesNotExist:
            raise TemplateDoesNotExist(template_name) from None

        # Get the active version of the template
        version = EmailTemplateVersion.objects.filter(
            template=record,
            is_active=True,
        ).first()

        if not version:
            raise TemplateDoesNotExist(template_name) from None

        return version.body

    def get_template_sources(self, template_name):
        """
        Yield possible template sources for the given template name.

        Args:
            template_name: The name/identifier of the template

        Yields:
            Origin: An Origin object representing the template source
        """
        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )
