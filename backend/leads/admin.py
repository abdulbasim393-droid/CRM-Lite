from django.contrib import admin

from .models import Lead, LeadSource


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "company",
        "status",
        "priority",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "source",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "company",
    )

    autocomplete_fields = (
        "assigned_to",
        "created_by",
        "source",
    )

    ordering = (
        "-created_at",
    )