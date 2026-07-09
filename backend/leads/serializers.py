from rest_framework import serializers

from .models import Lead, LeadSource


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = "__all__"


class LeadSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(
        source="source.name",
        read_only=True,
    )

    assigned_to_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = "__all__"

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None