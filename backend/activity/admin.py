from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "entity_type",
        "entity_id",
        "action",
        "performed_by",
        "created_at",
    )
    list_filter = (
        "entity_type",
        "action",
        "created_at",
    )
    search_fields = (
        "entity_type",
        "action",
    )
    readonly_fields = (
        "id",
        "entity_type",
        "entity_id",
        "action",
        "old_value",
        "new_value",
        "performed_by",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
