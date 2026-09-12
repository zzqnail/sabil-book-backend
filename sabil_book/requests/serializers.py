from rest_framework import serializers

from .models import Request


class RequestSerializer(serializers.ModelSerializer[Request]):
    class Meta:
        model = Request
        fields = [
            "id",
            "customer",
            "category",
            "title",
            "description",
            "budget",
            "status",
            "moderation_flags",
            "rejection_reason",
            "created_at",
            "updated_at",
            "published_at",
            "closed_at",
        ]
        read_only_fields = [
            "customer",
            "status",
            "moderation_flags",
            "rejection_reason",
            "created_at",
            "updated_at",
            "published_at",
            "closed_at",
        ]

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.status not in {
            Request.RequestStatus.DRAFT,
            Request.RequestStatus.REJECTED,
        }:
            msg = "Only a draft or rejected request can be edited."
            raise serializers.ValidationError(msg)
        return attrs


class BrowseRequestSerializer(serializers.ModelSerializer[Request]):
    class Meta:
        model = Request
        fields = [
            "id",
            "category",
            "title",
            "description",
            "budget",
            "status",
            "published_at",
            "closed_at",
        ]


class RejectionSerializer(serializers.Serializer):
    reason = serializers.CharField(allow_blank=False, trim_whitespace=True)
