from django.conf import settings
from django.db import models

from core.models import BaseModel
from leads.models import Lead


class FollowUpStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class FollowUp(BaseModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="follow_ups",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="follow_ups",
    )

    follow_up_at = models.DateTimeField()

    purpose = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=FollowUpStatus.choices,
        default=FollowUpStatus.PENDING,
    )

    outcome = models.TextField(
        blank=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("follow_up_at",)
        verbose_name = "Follow Up"
        verbose_name_plural = "Follow Ups"

    def __str__(self):
        return (
            f"{self.lead.first_name} "
            f"{self.lead.last_name} - "
            f"{self.follow_up_at:%d-%m-%Y %H:%M}"
        )