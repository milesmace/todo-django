from django.conf import settings
from django.template.backends.base import BaseEngine
from django.template.engine import Engine
from django.template.exceptions import TemplateDoesNotExist

from .template import DBEmailTemplate


class DBEmailTemplateEngine(BaseEngine):
    """
    A template engine that loads templates from the database.

    Template tag libraries can be configured via OPTIONS:
    - 'libraries': Dict of library names to module paths (e.g., {'email_tags': 'core.templatetags.email_tags'})
    - 'library_discovery_function': Optional callable that returns a dict of discovered libraries
                                    If provided, its result will be merged with 'libraries'
    """

    def __init__(self, params):
        params = params.copy()
        options = params.pop("OPTIONS", {}).copy()
        options.setdefault("autoescape", True)
        options.setdefault("debug", settings.DEBUG)
        options.setdefault("file_charset", "utf-8")

        # Handle template tag libraries configuration
        libraries = options.pop("libraries", {})
        library_discovery_function = options.pop("library_discovery_function", None)

        # If a discovery function is provided, use it to discover libraries
        if library_discovery_function is not None:
            if callable(library_discovery_function):
                discovered_libraries = library_discovery_function()
                # Merge discovered libraries with explicitly provided ones
                # Explicit libraries take precedence
                discovered_libraries.update(libraries)
                libraries = discovered_libraries
            else:
                raise ValueError(
                    "library_discovery_function must be a callable that returns a dict"
                )

        # Set libraries in options (empty dict if none provided)
        options["libraries"] = libraries

        super().__init__(
            {
                "NAME": params.get("NAME"),
                "DIRS": params.get("DIRS"),
                "APP_DIRS": params.get("APP_DIRS"),
            }
        )

        # Build the loader list: database loader first, then filesystem/app_directories as fallback
        loaders = ["db_email.loader.DBEmailTemplateLoader"]

        # Add filesystem loader if DIRS is configured
        if self.dirs:
            loaders.append("django.template.loaders.filesystem.Loader")

        # Add app_directories loader if APP_DIRS is enabled
        if self.app_dirs:
            loaders.append("django.template.loaders.app_directories.Loader")

        # Wrap in cached loader for performance (Django's default behavior)
        loaders = [("django.template.loaders.cached.Loader", loaders)]

        # Create a Django Engine instance with our custom loader first, then fallbacks
        # This ensures that {% extends %} and {% include %} try database first, then filesystem
        # Note: When loaders is provided, app_dirs must be False to avoid ImproperlyConfigured error
        # (we handle app_directories manually in the loaders list above)
        self.engine = Engine(
            self.dirs,
            app_dirs=False,  # Must be False when loaders is provided
            loaders=loaders,
            **options,
        )

    def from_string(self, template_code):
        # Use the engine's from_string method, which will use our custom loader
        # for any {% extends %} or {% include %} tags
        return DBEmailTemplate(
            template=self.engine.from_string(template_code),
            backend=self,
        )

    def get_template(self, template_name):
        try:
            # Use the engine's get_template method, which will use our custom loader
            return DBEmailTemplate(
                template=self.engine.get_template(template_name),
                backend=self,
            )
        except TemplateDoesNotExist as exc:
            # Re-raise with backend information
            exc.backend = self
            raise
