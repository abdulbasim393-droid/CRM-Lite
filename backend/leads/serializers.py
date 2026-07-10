from rest_framework import serializers
from core.choices import UserRole
from .models import Lead, LeadSource, LeadNote


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
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "company",
            "job_title",
            "website",
            "source",
            "source_name",
            "status",
            "priority",
            "estimated_value",
            "assigned_to",
            "assigned_to_name",
            "created_by",
            "created_at",
            "updated_at",
            "is_active",
        )

        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "source_name",
            "assigned_to_name",
        )

    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.email
        return None

    def validate_phone(self, value):
        queryset = Lead.objects.filter(
            phone=value,
            is_active=True,
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "An active lead with this phone number already exists."
            )

        return value

    def validate_email(self, value):
        if not value:
            return value

        queryset = Lead.objects.filter(
            email=value,
            is_active=True,
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "An active lead with this email already exists."
            )

        return value

    def validate_assigned_to(self, value):
        if value is None:
            return value

        if value.role != UserRole.SALES_EXECUTIVE:
            raise serializers.ValidationError(
                "Leads can only be assigned to a Sales Executive."
        )

        return value   



    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request:
            user = request.user

            if user.role == user.Role.SALES_EXECUTIVE:
                restricted_fields = ["assigned_to", "created_by"]

                for field in restricted_fields:
                    if field in validated_data:
                        raise serializers.ValidationError(
                            {
                                field: "You are not allowed to modify this field."
                            }
                        )

        return super().update(instance, validated_data)



class LeadNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = LeadNote
        fields = (
            "id",
            "lead",
            "note_type",
            "note_text",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.email