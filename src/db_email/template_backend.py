from django.template.backends.base import BaseEngine
from django.template.exceptions import TemplateDoesNotExist

from .models import EmailTemplate
from .template import DBEmailTemplate


class DBEmailTemplateEngine(BaseEngine):
    def __init__(self, params):
        super().__init__(
            {
                "NAME": params.get("NAME"),
                "DIRS": params.get("DIRS"),
                "APP_DIRS": params.get("APP_DIRS"),
            }
        )

    def from_string(self, template_code):
        return DBEmailTemplate(
            source=template_code,
            engine=self,
        )

    def get_template(self, template_name):
        try:
            record = EmailTemplate.objects.get(identifier=template_name)
        except EmailTemplate.DoesNotExist:
            raise TemplateDoesNotExist(template_name) from None

        return DBEmailTemplate(
            source=record.body,
            engine=self,
            metadata={"identifier": record.identifier},
        )
