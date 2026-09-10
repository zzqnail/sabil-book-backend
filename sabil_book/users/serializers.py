from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from sabil_book.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }


class RegisterSerializer(serializers.ModelSerializer[User]):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["email", "password", "name", "country"]

    def create(self, validated_data: dict) -> User:
        return User.objects.create_user(**validated_data)
