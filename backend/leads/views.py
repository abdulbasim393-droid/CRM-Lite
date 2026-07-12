from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from core.choices import LeadStatus, UserRole

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from customers.models import Customer
from customers.serializers import CustomerSerializer


from rest_framework.exceptions import PermissionDenied, ValidationError


from rest_framework.permissions import IsAuthenticated

from .permissions import LeadPermission
from .serializers import (
    LeadSerializer,
    LeadSourceSerializer,
)


from .models import (
    Lead,
    LeadSource,
    LeadNote,
)


from leads.serializers import LeadNoteSerializer


from activity.services import log_activity
from activity.models import (
    ActivityLog,
    EntityType,
    ActionType,
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
            lead = serializer.save(
                created_by=user,
                assigned_to=user,
            )   
        else:
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

            lead = serializer.save(created_by=user)

        log_activity(
            entity_type=EntityType.LEAD,
            entity_id=lead.id,
            action=ActionType.CREATED,
            performed_by=user,
            new_value={
                "status": lead.status,
                "assigned_to": (
                    lead.assigned_to.email
                    if lead.assigned_to
                    else None
                ),
            },
        )

    def perform_update(self, serializer):
        lead = serializer.instance
        old_status = lead.status
        old_assigned_to = lead.assigned_to

        lead = serializer.save()

        log_activity(
            entity_type=EntityType.LEAD,
            entity_id=lead.id,
            action=ActionType.UPDATED,
            performed_by=self.request.user,
            old_value={
                "status": old_status,
                "assigned_to": old_assigned_to.email if old_assigned_to else None,
            },
            new_value={
                "status": lead.status,
                "assigned_to": lead.assigned_to.email if lead.assigned_to else None,
            },
        )

    def perform_destroy(self, instance):
        log_activity(
            entity_type=EntityType.LEAD,
            entity_id=instance.id,
            action=ActionType.DELETED,
            performed_by=self.request.user,
            old_value={
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "email": instance.email,
            },
        )
        instance.delete()

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
        

    @action(
    detail=True,
    methods=["post"],
    )
    @transaction.atomic
    def convert(self, request, pk=None):
        lead = self.get_object()

        if lead.status != LeadStatus.WON:
            return Response(
                {
                    "detail": "Only leads with status 'WON' can be converted."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Customer.objects.filter(lead=lead).exists():
            return Response(
                {
                    "detail": "This lead has already been converted."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer = Customer.objects.create(
            lead=lead,
            first_name=lead.first_name,
            last_name=lead.last_name,
            phone=lead.phone,
            email=lead.email,
            company=lead.company,
            created_by=request.user,
        )

        log_activity(
            entity_type=EntityType.LEAD,
            entity_id=lead.id,
            action=ActionType.CONVERTED,
            performed_by=request.user,
            old_value={"status": LeadStatus.WON},
            new_value={
                "customer_id": str(customer.id),
            },
        )

        log_activity(
            entity_type=EntityType.CUSTOMER,
            entity_id=customer.id,
            action=ActionType.CREATED,
            performed_by=request.user,
            new_value={
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "email": customer.email,
                "company": customer.company,
            },
        )

        serializer = CustomerSerializer(
                customer,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )



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

        note = serializer.save(created_by=user)

        log_activity(
            entity_type=EntityType.LEAD_NOTE,
            entity_id=note.id,
            action=ActionType.CREATED,
            performed_by=user,
            new_value={
                "lead_id": str(lead.id),
                "note_type": note.note_type,
            },
        )

    def perform_update(self, serializer):
        note = serializer.instance
        old_note_type = note.note_type
        old_note_text = note.note_text

        note = serializer.save()

        log_activity(
            entity_type=EntityType.LEAD_NOTE,
            entity_id=note.id,
            action=ActionType.UPDATED,
            performed_by=self.request.user,
            old_value={
                "note_type": old_note_type,
                "note_text": old_note_text,
            },
            new_value={
                "note_type": note.note_type,
                "note_text": note.note_text,
            },
        )

    def perform_destroy(self, instance):
        log_activity(
            entity_type=EntityType.LEAD_NOTE,
            entity_id=instance.id,
            action=ActionType.DELETED,
            performed_by=self.request.user,
            old_value={
                "lead_id": str(instance.lead_id),
                "note_type": instance.note_type,
            },
        )
        instance.delete()