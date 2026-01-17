from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """Called when the app is ready. Connect signals here."""
        # Import and connect the CORS signal handler
        from .cors import connect_cors_signal

        connect_cors_signal()

        # Import sysconfig to register configuration
        from . import sysconfig  # noqa: F401
