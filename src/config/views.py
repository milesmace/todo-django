"""
Admin Views for Configuration Management

These views provide the admin interface for managing app configurations.
They are integrated into Django's admin site and require admin permissions.
"""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .frontend_models import get_frontend_model
from .models import ConfigValue
from .registry import config_registry


@method_decorator(staff_member_required, name="dispatch")
class ConfigAppListView(View):
    """
    View to list all apps that have registered configurations.
    """

    template_name = "config/app_list.html"

    def get(self, request):
        configs = config_registry.get_all_configs()

        # Build list of apps with their metadata
        apps = []
        for app_label, config_def in sorted(configs.items()):
            section_count = len(config_def.sections)
            field_count = sum(
                len(section.get_fields()) for section in config_def.sections.values()
            )
            apps.append(
                {
                    "app_label": app_label,
                    "section_count": section_count,
                    "field_count": field_count,
                }
            )

        context = {
            "title": "System Configuration",
            "apps": apps,
            "has_permission": True,
            "site_header": "Django administration",
            "site_title": "Django site admin",
        }
        return render(request, self.template_name, context)


@method_decorator(staff_member_required, name="dispatch")
class ConfigAppDetailView(View):
    """
    View to display and edit configurations for a specific app.

    Renders all sections and fields for the app, allowing admins to
    modify configuration values.
    """

    template_name = "config/app_config.html"

    def get(self, request, app_label):
        config_def = config_registry.get_config(app_label)
        if not config_def:
            messages.error(request, f"No configuration found for app: {app_label}")
            return redirect("config:app_list")

        sections_data = self._build_sections_data(app_label, config_def)

        context = {
            "title": f"Configuration: {app_label}",
            "app_label": app_label,
            "sections": sections_data,
            "has_permission": True,
            "site_header": "Django administration",
            "site_title": "Django site admin",
        }
        return render(request, self.template_name, context)

    def post(self, request, app_label):
        config_def = config_registry.get_config(app_label)
        if not config_def:
            messages.error(request, f"No configuration found for app: {app_label}")
            return redirect("config:app_list")

        # Process each field in the configuration
        saved_count = 0
        for section_name, section in config_def.get_sections():
            section_key = section_name.lower()
            for field_name, field in section.get_fields().items():
                path = f"{section_key}/{field_name}"
                input_name = f"config_{section_key}_{field_name}"

                # Get the frontend model to process the value
                frontend_model = get_frontend_model(
                    field.frontend_model,
                    field,
                    None,
                )

                # Get raw value from POST (handle checkbox specially)
                raw_value = request.POST.get(input_name)

                # Convert and serialize the value
                processed_value = frontend_model.get_value(raw_value)
                serialized_value = frontend_model.serialize_value(processed_value)

                # Save to database
                ConfigValue.objects.update_or_create(
                    app_label=app_label,
                    path=path,
                    defaults={"value": serialized_value},
                )
                saved_count += 1

        messages.success(
            request,
            f"Configuration saved successfully. ({saved_count} settings updated)",
        )
        return redirect("config:app_detail", app_label=app_label)

    def _build_sections_data(self, app_label: str, config_def) -> list[dict]:
        """Build the sections data structure for the template."""
        # Fetch all stored values for this app
        stored_values = {
            cv.path: cv.value for cv in ConfigValue.objects.filter(app_label=app_label)
        }

        sections_data = []
        for section_name, section in config_def.get_sections():
            section_key = section_name.lower()
            fields_data = []

            for field_name, field in section.get_fields().items():
                path = f"{section_key}/{field_name}"

                # Get stored value or use default
                stored_value = stored_values.get(path)
                if stored_value is None:
                    current_value = field.default
                else:
                    current_value = stored_value

                # Get the frontend model and render the input
                frontend_model = get_frontend_model(
                    field.frontend_model,
                    field,
                    current_value,
                )

                fields_data.append(
                    {
                        "name": field_name,
                        "field": field,
                        "rendered_input": frontend_model.render(),
                        "has_stored_value": stored_value is not None,
                    }
                )

            sections_data.append(
                {
                    "name": section_name,
                    "label": section.label or section_name,
                    "sort_order": section.sort_order,
                    "fields": fields_data,
                }
            )

        return sections_data
