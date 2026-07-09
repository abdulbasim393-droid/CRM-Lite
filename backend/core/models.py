import uuid

from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields, and uses UUID
    as the primary key instead of the default auto-incrementing ID.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this object."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="The date and time this object was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="The date and time this object was last updated."
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]
