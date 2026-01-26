from config.accessor import config
from django import template

register = template.Library()


@register.inclusion_tag("email_footer")
def email_footer():
    return {
        "APP_URL": config.get("core.app.react_app_url"),
        "CONTACT_EMAIL": config.get("core.app.contact_email"),
        "HELP_URL": "https://example.com/help",
    }
