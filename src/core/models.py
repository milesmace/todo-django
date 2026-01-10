from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model where email is the unique identifier for authentication.
    """

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(
        max_length=255, blank=True, help_text="Display name for the user"
    )
    timezone = models.CharField(
        max_length=50, default="UTC", help_text="User's timezone"
    )
    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional user data stored as JSON"
    )

    # Admin and authentication fields
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text="Designates that this user has all permissions without "
        "explicitly assigning them.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is already required

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the display name."""
        return self.name or self.email

    def get_short_name(self):
        """Return the display name."""
        return self.name or self.email

    def get_metadata(self, key, default=None):
        """Helper method to get a value from metadata."""
        return self.metadata.get(key, default)

    def set_metadata(self, key, value):
        """Helper method to set a value in metadata."""
        if not isinstance(self.metadata, dict):
            self.metadata = {}
        self.metadata[key] = value
        self.save(update_fields=["metadata"])

    def get_security_metadata(self):
        """Get security-related metadata."""
        security = self.metadata.get("security", {})
        return {
            "email_verified": security.get("email_verified", False),
            "email_verified_at": security.get("email_verified_at"),
            "password_changed_at": security.get("password_changed_at"),
        }

    def set_security_metadata(self, **kwargs):
        """Set security-related metadata."""
        if "security" not in self.metadata or not isinstance(
            self.metadata["security"], dict
        ):
            self.metadata["security"] = {}

        for key, value in kwargs.items():
            if key in ["email_verified", "email_verified_at", "password_changed_at"]:
                self.metadata["security"][key] = value

        self.save(update_fields=["metadata"])
