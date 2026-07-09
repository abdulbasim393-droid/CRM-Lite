from django.conf import settings
from django.db import models

from core.choices import LeadPriority, LeadStatus
from core.models import BaseModel
from .lead_source import LeadSource


class Lead(BaseModel):
    """
    Represents a potential customer in the CRM.
    """

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
    )

    company = models.CharField(
        max_length=255,
        blank=True,
    )

    job_title = models.CharField(
        max_length=150,
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    source = models.ForeignKey(
        LeadSource,
        on_delete=models.PROTECT,
        related_name="leads",
    )

    status = models.CharField(
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        db_index=True,
    )

    priority = models.CharField(
        max_length=20,
        choices=LeadPriority.choices,
        default=LeadPriority.MEDIUM,
        db_index=True,
    )

    estimated_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_leads",
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["created_at"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.full_name