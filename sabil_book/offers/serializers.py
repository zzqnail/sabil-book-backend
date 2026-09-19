from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer[Message]):
    class Meta:
        model = Message
        fields = ["id", "offer", "sender", "body", "date_time"]
        read_only_fields = fields
