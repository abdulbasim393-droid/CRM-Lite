from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """Choices for user roles within the system."""
    ADMIN = "ADMIN", _("Admin")
    SALES_MANAGER = "SALES_MANAGER", _("Sales Manager")
    SALES_EXECUTIVE = "SALES_EXECUTIVE", _("Sales Executive")


class LeadStatus(models.TextChoices):
    """Choices for tracking the status of a lead."""
    NEW = "NEW", _("New")
    CONTACTED = "CONTACTED", _("Contacted")
    DEMO = "DEMO", _("Demo")
    NEGOTIATION = "NEGOTIATION", _("Negotiation")
    WON = "WON", _("Won")
    LOST = "LOST", _("Lost")


class LeadPriority(models.TextChoices):
    """Choices for setting the priority of a lead."""
    LOW = "LOW", _("Low")
    MEDIUM = "MEDIUM", _("Medium")
    HIGH = "HIGH", _("High")
    URGENT = "URGENT", _("Urgent")


class FollowUpStatus(models.TextChoices):
    """Choices for tracking the status of follow-up tasks."""
    PENDING = "PENDING", _("Pending")
    COMPLETED = "COMPLETED", _("Completed")
    MISSED = "MISSED", _("Missed")



class LeadSourceType(models.TextChoices):
    WEBSITE = "WEBSITE", _("Website")
    REFERRAL = "REFERRAL", _("Referral")
    SOCIAL_MEDIA = "SOCIAL_MEDIA", _("Social Media")
    EMAIL = "EMAIL", _("Email")
    PHONE = "PHONE", _("Phone")
    WALK_IN = "WALK_IN", _("Walk In")
    OTHER = "OTHER", _("Other")