from django.conf import settings
from django.db import models

from core.models import BaseModel
from leads.models import Lead


class Customer(BaseModel):
    lead = models.OneToOneField(
        Lead,
        on_delete=models.PROTECT,
        related_name="customer",
    )

    first_name = models.CharField(max_length=100)

    last_name = models.CharField(
        max_length=100,
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        unique=True,
    )

    email = models.EmailField(
        blank=True,
        null=True,
    )

    company = models.CharField(
        max_length=255,
        blank=True,
    )

    address = models.TextField(
        blank=True,
    )

    converted_at = models.DateTimeField(
        auto_now_add=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="customers_created",
    )

    class Meta:
        ordering = ("-converted_at",)
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()