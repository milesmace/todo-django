from django.template.context import make_context
from django.template.exceptions import TemplateDoesNotExist


class DBEmailTemplate:
    """
    A template wrapper that uses the custom database template engine.

    This class wraps a Django Template object created by our custom engine,
    ensuring that {% extends %} and {% include %} tags use the database loader.
    """

    def __init__(self, template, backend, metadata=None):
        """
        Initialize the template wrapper.

        Args:
            template: The Django Template object created by the engine
            backend: The DBEmailTemplateEngine instance
            metadata: Optional metadata dictionary
        """
        self.template = template
        self.backend = backend
        self.metadata = metadata or {}

    @property
    def origin(self):
        """Return the template origin for debugging."""
        return self.template.origin

    def render(self, context=None, request=None):
        """
        Render the template with the given context.

        Args:
            context: A dict or Context object
            request: Optional request object

        Returns:
            str: The rendered template
        """
        # Use make_context to properly handle context creation
        # This ensures compatibility with Django's context processors
        context = make_context(
            context,
            request,
            autoescape=self.backend.engine.autoescape,
        )

        try:
            return self.template.render(context)
        except TemplateDoesNotExist as exc:
            # Re-raise with backend information
            exc.backend = self.backend
            raise
