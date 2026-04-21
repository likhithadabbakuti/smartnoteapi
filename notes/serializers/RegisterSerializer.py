from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=("user", "staff"),
        required=False,
        default="user",
    )
    staff_registration_key = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def validate(self, attrs):
        role = attrs.get("role", "user")

        if role == "staff":
            provided_key = attrs.get("staff_registration_key", "")
            expected_key = settings.STAFF_REGISTRATION_KEY

            if not expected_key or provided_key != expected_key:
                raise serializers.ValidationError(
                    {"role": "Invalid or missing staff registration key."}
                )

        return attrs

    def create(self, validated_data):
        role = validated_data.pop("role", "user")
        validated_data.pop("staff_registration_key", None)
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            is_staff=(role == "staff"),
        )
