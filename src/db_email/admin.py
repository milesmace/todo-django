from django import forms
from django.contrib import admin
from django.db import transaction

from .models import EmailTemplate, EmailTemplateVersion


class EmailTemplateAdminForm(forms.ModelForm):
    """
    Custom form for EmailTemplate admin with active version dropdown.

    Provides a convenient dropdown to select which version should be active.
    """

    active_version_select = forms.ChoiceField(
        required=False,
        label="Active Version",
        help_text="Select which version should be active for this template.",
    )

    class Meta:
        model = EmailTemplate
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show the dropdown for existing templates (not on create)
        if self.instance and self.instance.pk:
            # Get all versions for this template
            versions = EmailTemplateVersion.objects.filter(
                template=self.instance
            ).order_by("-created_at")

            # Build choices: (pk, "version_name (subject preview)")
            choices = [("", "--- Select Active Version ---")]
            for version in versions:
                subject_preview = (
                    version.subject[:30] + "..."
                    if len(version.subject) > 30
                    else version.subject
                )
                label = f"{version.version} - {subject_preview}"
                if version.is_active:
                    label += " (current)"
                choices.append((str(version.pk), label))

            self.fields["active_version_select"].choices = choices

            # Set the current value
            active = versions.filter(is_active=True).first()
            if active:
                self.initial["active_version_select"] = str(active.pk)
        else:
            # Hide the field for new templates
            self.fields["active_version_select"].widget = forms.HiddenInput()


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateAdminForm
    list_display = [
        "identifier",
        "active_version_display",
        "version_count",
        "created_at",
        "updated_at",
    ]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["identifier"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at", "version_count_display"]

    fieldsets = (
        (None, {"fields": ("identifier",)}),
        (
            "Version Management",
            {
                "fields": ("active_version_select", "version_count_display"),
                "description": "Select the active version for this template.",
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Active Version")
    def active_version_display(self, obj):
        """Display the currently active version for this template."""
        version = EmailTemplateVersion.objects.filter(
            template=obj, is_active=True
        ).first()
        return version.version if version else "None"

    @admin.display(description="Versions")
    def version_count(self, obj):
        """Display the total number of versions for this template."""
        return EmailTemplateVersion.objects.filter(template=obj).count()

    @admin.display(description="Total Versions")
    def version_count_display(self, obj):
        """Display version count as a readonly field in the form."""
        if obj and obj.pk:
            count = EmailTemplateVersion.objects.filter(template=obj).count()
            return f"{count} version(s)"
        return "N/A"

    def get_fieldsets(self, request, obj=None):
        """Hide version management fieldset for new templates."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            # Remove the "Version Management" fieldset for new templates
            return tuple(fs for fs in fieldsets if fs[0] != "Version Management")
        return fieldsets

    def save_model(self, request, obj, form, change):
        """
        Save the model and handle active version selection.

        This is called after the form's save() with commit=True,
        so we handle the active version logic here.
        """
        super().save_model(request, obj, form, change)

        # Handle active version selection (only for existing templates)
        if change and obj.pk:
            selected_pk = form.cleaned_data.get("active_version_select")
            if selected_pk:
                with transaction.atomic():
                    # Deactivate all versions for this template
                    EmailTemplateVersion.objects.filter(template=obj).update(
                        is_active=False
                    )
                    # Activate the selected version
                    EmailTemplateVersion.objects.filter(pk=selected_pk).update(
                        is_active=True
                    )


@admin.register(EmailTemplateVersion)
class EmailTemplateVersionAdmin(admin.ModelAdmin):
    list_display = [
        "template",
        "version",
        "is_active",
        "subject",
        "created_at",
        "updated_at",
    ]
    list_filter = ["is_active", "template", "created_at", "updated_at"]
    search_fields = ["template__identifier", "version", "subject", "body"]
    sortable_by = ["template", "version", "is_active", "created_at", "updated_at"]
    ordering = ["-created_at"]
    readonly_fields = ["is_active", "created_at", "updated_at"]
