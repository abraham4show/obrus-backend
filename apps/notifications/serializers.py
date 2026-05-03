from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    related_object_type = serializers.SerializerMethodField()
    related_object_id = serializers.UUIDField(source='object_id', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'message', 'is_read', 'related_object_type',
            'related_object_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_related_object_type(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return None


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']
