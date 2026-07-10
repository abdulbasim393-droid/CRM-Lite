from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Lead, LeadSource
from .permissions import LeadPermission
from .serializers import (
    LeadSerializer,
    LeadSourceSerializer,
)


class LeadSourceViewSet(viewsets.ModelViewSet):
    queryset = LeadSource.objects.all()

    serializer_class = LeadSourceSerializer

    permission_classes = [LeadPermission]


class LeadViewSet(viewsets.ModelViewSet):
    queryset = (
        Lead.objects
        .select_related(
            "source",
            "assigned_to",
            "created_by",
        )
        .all()
    )

    serializer_class = LeadSerializer

    permission_classes = [LeadPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "status",
        "priority",
        "source",
        "assigned_to",
    ]

    search_fields = [
        "first_name",
        "last_name",
        "email",
        "phone",
        "company",
    ]

    ordering_fields = [
        "created_at",
        "estimated_value",
        "status",
        "priority",
    ]

    ordering = ["-created_at"]