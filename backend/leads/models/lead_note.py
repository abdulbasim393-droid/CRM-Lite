from django.conf import settings
from django.db import models

from core.models import BaseModel
from .lead import Lead


class NoteType(models.TextChoices):
    CALL = "CALL", "Call"
    WHATSAPP = "WHATSAPP", "WhatsApp"
    MEETING = "MEETING", "Meeting"
    DEMO = "DEMO", "Demo"
    OBJECTION = "OBJECTION", "Objection"
    OTHER = "OTHER", "Other"


class LeadNote(BaseModel):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lead_notes",
    )

    note_type = models.CharField(
        max_length=20,
        choices=NoteType.choices,
        default=NoteType.OTHER,
    )

    note_text = models.TextField()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Lead Note"
        verbose_name_plural = "Lead Notes"

    def __str__(self):
        return (
            f"{self.get_note_type_display()} - "
            f"{self.lead.first_name} {self.lead.last_name}"
        )