"""
Helper functions for retrieving configuration values.

This module provides convenient functions to access stored configuration
values throughout your application.
"""

from typing import Any

from .models import ConfigValue
from .registry import config_registry


def get_config(app_label: str, path: str, default: Any = None) -> Any:
    """
    Get a configuration value for an app.

    Args:
        app_label: The app label (e.g., 'todo')
        path: The configuration path (e.g., 'general/max_todos_per_user')
        default: Default value if not found (overrides field default)

    Returns:
        The configuration value, or the default if not found

    Example:
        >>> get_config('todo', 'general/max_todos_per_user')
        100
        >>> get_config('todo', 'display/items_per_page', default=10)
        20
    """
    # Try to get stored value from database
    try:
        config_value = ConfigValue.objects.get(app_label=app_label, path=path)
        if config_value.value is not None:
            return config_value.value
    except ConfigValue.DoesNotExist:
        pass

    # Fall back to field default from registry
    config_def = config_registry.get_config(app_label)
    if config_def:
        field = config_def.get_field(path)
        if field and field.default is not None:
            return field.default

    # Finally, use provided default
    return default


def get_config_int(app_label: str, path: str, default: int = 0) -> int:
    """Get a configuration value as an integer."""
    value = get_config(app_label, path, default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_config_bool(app_label: str, path: str, default: bool = False) -> bool:
    """Get a configuration value as a boolean."""
    value = get_config(app_label, path, default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")
    return bool(value)


def get_config_float(app_label: str, path: str, default: float = 0.0) -> float:
    """Get a configuration value as a float."""
    value = get_config(app_label, path, default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
