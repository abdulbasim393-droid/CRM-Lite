from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from core.choices import UserRole

from rest_framework.exceptions import PermissionDenied

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
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


    

    def get_queryset(self):
        user = self.request.user

        queryset = self.queryset

        if not user.is_authenticated:
            return queryset.none()

        if user.role in (
            UserRole.ADMIN,
            UserRole.SALES_MANAGER,
        ):
            return queryset

        return queryset.filter(
            assigned_to=user,
        )

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == UserRole.SALES_EXECUTIVE:
            serializer.save(
                created_by=user,
                assigned_to=user,
            )
            return

        assigned_to = serializer.validated_data.get("assigned_to")

        if assigned_to is None:
            raise ValidationError(
                {
                    "assigned_to": (
                        "Admin and Sales Manager must assign the lead "
                        "to a Sales Executive."
                    )
            }
        )

        serializer.save(created_by=user)


    def get_permissions(self):
        if self.action == "destroy" and self.request.user.is_authenticated:
            if self.request.user.role not in (
                UserRole.ADMIN,
                UserRole.SALES_MANAGER,
            ):
                raise ValidationError(
                    "You do not have permission to delete leads."
                )
        return [IsAuthenticated()]
        


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserRole
from leads.models import Lead, LeadNote
from leads.serializers import LeadNoteSerializer


class LeadNoteViewSet(viewsets.ModelViewSet):
    queryset = LeadNote.objects.none()
    serializer_class = LeadNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = LeadNote.objects.select_related(
            "lead",
            "created_by",
        )

        if not user.is_authenticated:
            return queryset.none()

        if user.role in (
            UserRole.ADMIN,
            UserRole.SALES_MANAGER,
        ):
            return queryset

        return queryset.filter(
            lead__assigned_to=user,
        )

    def perform_create(self, serializer):
        lead = serializer.validated_data["lead"]
        user = self.request.user

        if (
            user.role == UserRole.SALES_EXECUTIVE
            and lead.assigned_to != user
        ):
            raise PermissionDenied(
                "You can only add notes to your assigned leads."
            )

        serializer.save(created_by=user)