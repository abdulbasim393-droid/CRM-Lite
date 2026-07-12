import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class EntityType(models.TextChoices):
    LEAD = "LEAD", _("Lead")
    LEAD_NOTE = "LEAD_NOTE", _("Lead Note")
    CUSTOMER = "CUSTOMER", _("Customer")
    FOLLOW_UP = "FOLLOW_UP", _("Follow Up")
    USER = "USER", _("User")


class ActionType(models.TextChoices):
    CREATED = "CREATED", _("Created")
    UPDATED = "UPDATED", _("Updated")
    DELETED = "DELETED", _("Deleted")
    CONVERTED = "CONVERTED", _("Converted")
    COMPLETED = "COMPLETED", _("Completed")
    ASSIGNED = "ASSIGNED", _("Assigned")


class ActivityLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    entity_type = models.CharField(
        max_length=20,
        choices=EntityType.choices,
        db_index=True,
    )
    entity_id = models.UUIDField(
        db_index=True,
    )
    action = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        db_index=True,
    )
    old_value = models.JSONField(
        null=True,
        blank=True,
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Activity Log")
        verbose_name_plural = _("Activity Logs")
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        return f"{self.action} {self.entity_type} ({self.entity_id})"
