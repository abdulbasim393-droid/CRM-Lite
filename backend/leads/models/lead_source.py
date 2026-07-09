from django.db import models

from core.models import BaseModel


class LeadSource(BaseModel):
    """
    Represents where a lead originated.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Lead Source"
        verbose_name_plural = "Lead Sources"

    def __str__(self):
        return self.name