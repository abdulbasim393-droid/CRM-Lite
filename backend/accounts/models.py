from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.choices import UserRole
from core.models import BaseModel
from .managers import UserManager


class User(BaseModel, AbstractUser):
    """
    Custom user model inheriting from AbstractUser and BaseModel.
    Uses email as the primary unique identifier for authentication.
    """
    username = None  # Remove the default username field
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        _("user role"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.SALES_EXECUTIVE,
        help_text=_("Designates the user's role in the system."),
        db_index=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.get_full_name() or self.email