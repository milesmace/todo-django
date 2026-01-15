from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "password", "name", "timezone"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            timezone=validated_data.get("timezone", "UTC"),
        )
        return user


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification."""

    token = serializers.CharField(required=True, help_text="Email verification token")


class ResendVerificationEmailSerializer(serializers.Serializer):
    """Serializer for resending verification email."""

    email = serializers.EmailField(
        required=True, help_text="Email address to resend verification to"
    )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return value

        # Check if already verified
        security = user.get_security_metadata()
        if security.get("email_verified"):
            raise serializers.ValidationError("Email is already verified.")

        return value


class UserSecuritySerializer(serializers.Serializer):
    """Serializer for user security metadata."""

    email_verified = serializers.BooleanField(read_only=True)
    email_verified_at = serializers.DateTimeField(read_only=True, allow_null=True)
