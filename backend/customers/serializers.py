from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = (
            "id",
            "lead",
            "first_name",
            "last_name",
            "phone",
            "email",
            "company",
            "address",
            "created_by",
            "created_by_name",
            "converted_at",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "lead",
            "created_by",
            "created_by_name",
            "converted_at",
            "created_at",
            "updated_at",
        )

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.email