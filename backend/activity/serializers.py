from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "entity_type",
            "entity_id",
            "action",
            "old_value",
            "new_value",
            "performed_by",
            "performed_by_name",
            "created_at",
        )

        read_only_fields = fields

    def get_performed_by_name(self, obj):
        return obj.performed_by.get_full_name() or obj.performed_by.email