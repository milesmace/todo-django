"""
Utility functions for template configuration.

This module provides helper functions for configuring template engines,
including template tag library discovery.
"""

from importlib import import_module
from pkgutil import walk_packages

from django.apps import apps
from django.template.library import InvalidTemplateLibrary


def get_template_tag_modules():
    """
    Yield (module_name, module_path) pairs for all installed template tag
    libraries.
    """
    candidates = ["django.templatetags"]
    candidates.extend(
        f"{app_config.name}.templatetags" for app_config in apps.get_app_configs()
    )

    for candidate in candidates:
        try:
            pkg = import_module(candidate)
        except ImportError:
            # No templatetags package defined. This is safe to ignore.
            continue

        if hasattr(pkg, "__path__"):
            for name in get_package_libraries(pkg):
                yield name[len(candidate) + 1 :], name


def get_package_libraries(pkg):
    """
    Recursively yield template tag libraries defined in submodules of a
    package.
    """
    for entry in walk_packages(pkg.__path__, pkg.__name__ + "."):
        try:
            module = import_module(entry[1])
        except ImportError as e:
            raise InvalidTemplateLibrary(
                f"Invalid template library specified. ImportError raised when "
                f"trying to load '{entry[1]}': {e}"
            ) from e

        if hasattr(module, "register"):
            yield entry[1]


def discover_template_tag_libraries():
    """
    Discover and return all template tag libraries from installed apps.

    Returns:
        dict: A dictionary mapping library names to their full module paths.
              Example: {'email_tags': 'core.templatetags.email_tags'}

    Usage:
        In settings.py:

        from core.template_utils import discover_template_tag_libraries

        TEMPLATES = [
            {
                "BACKEND": "db_email.template_backend.DBEmailTemplateEngine",
                "OPTIONS": {
                    "library_discovery_function": discover_template_tag_libraries,
                },
            },
        ]
    """
    return dict(get_template_tag_modules())
