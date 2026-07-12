from django.utils import timezone
from rest_framework import serializers

from core.choices import UserRole
from .models import FollowUp
from core.choices import LeadStatus


class FollowUpSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = FollowUp
        fields = (
            "id",
            "lead",
            "assigned_to",
            "assigned_to_name",
            "follow_up_at",
            "purpose",
            "status",
            "outcome",
            "completed_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "completed_at",
            "created_at",
            "updated_at",
            "assigned_to_name",
        )

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() or obj.assigned_to.email

    def validate_follow_up_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "Follow-up date and time cannot be in the past."
            )

        return value

    def validate_assigned_to(self, value):
        if value.role != UserRole.SALES_EXECUTIVE:
            raise serializers.ValidationError(
                "Follow-up can only be assigned to a Sales Executive."
            )

        return value

    def validate_lead(self, value):
        if value.status in (
            LeadStatus.WON,
            LeadStatus.LOST,
        ):
            raise serializers.ValidationError(
                "Cannot schedule follow-ups for WON or LOST leads."
            )

        return value