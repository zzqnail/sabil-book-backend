from django.contrib.auth.password_validation import validate_password
from django.db.models import Avg
from rest_framework import serializers

from sabil_book.reviews.models import Review
from sabil_book.users.models import ProviderProfile
from sabil_book.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["name", "country", "url"]

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


def _provider_rating(provider: ProviderProfile) -> float | None:
    average = Review.objects.filter(order__offer__provider=provider).aggregate(
        avg=Avg("rating"),
    )["avg"]
    return float(average) if average is not None else None


class ProviderProfilePublicSerializer(serializers.ModelSerializer[ProviderProfile]):
    """Public view of a provider: no payout details."""

    rating = serializers.SerializerMethodField()

    class Meta:
        model = ProviderProfile
        fields = ["id", "country", "kyc_status", "rating"]
        read_only_fields = fields

    def get_rating(self, obj: ProviderProfile) -> float | None:
        return _provider_rating(obj)


class ProviderProfileSerializer(serializers.ModelSerializer[ProviderProfile]):
    """Full view of a provider profile, for its owner only."""

    rating = serializers.SerializerMethodField()

    class Meta:
        model = ProviderProfile
        fields = ["id", "country", "payout_provider", "kyc_status", "rating"]
        read_only_fields = ["kyc_status"]

    def get_rating(self, obj: ProviderProfile) -> float | None:
        return _provider_rating(obj)
