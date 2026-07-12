from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.choices import UserRole

from activity.models import ActionType, EntityType
from activity.services import log_activity

from .models import FollowUp, FollowUpStatus
from .serializers import FollowUpSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter



class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    permission_classes = [IsAuthenticated]


    filter_backends = (
    DjangoFilterBackend,
    SearchFilter,
    OrderingFilter,
    )

    filterset_fields = (
        "status",
        "assigned_to",
    )

    search_fields = (
        "purpose",
        "outcome",
        "lead__first_name",
        "lead__last_name",
    )

    ordering_fields = (
        "follow_up_at",
        "created_at",
        "completed_at",
    )

    ordering = (
        "follow_up_at",
    )


    @action(
    detail=True,
    methods=["patch"],
    )
    def complete(self, request, pk=None):
        follow_up = self.get_object()

        if follow_up.status == FollowUpStatus.COMPLETED:
            return Response(
                {
                    "detail": "This follow-up is already completed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        outcome = request.data.get("outcome")

        if not outcome:
            return Response(
                {
                    "outcome": [
                        "This field is required."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_up.status = FollowUpStatus.COMPLETED
        follow_up.outcome = outcome
        follow_up.completed_at = timezone.now()
        follow_up.save()

        log_activity(
            entity_type=EntityType.FOLLOW_UP,
            entity_id=follow_up.id,
            action=ActionType.COMPLETED,
            performed_by=request.user,
            old_value={"status": FollowUpStatus.PENDING},
            new_value={
                "status": FollowUpStatus.COMPLETED,
                "outcome": outcome,
            },
        )

        serializer = self.get_serializer(follow_up)

        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        queryset = FollowUp.objects.select_related(
            "lead",
            "assigned_to",
        )

        if user.role in (
            UserRole.ADMIN,
            UserRole.SALES_MANAGER,
        ):
            return queryset

        return queryset.filter(
            assigned_to=user,
        )

    def perform_create(self, serializer):
        lead = serializer.validated_data["lead"]
        assigned_to = serializer.validated_data["assigned_to"]
        user = self.request.user

        if (
            user.role == UserRole.SALES_EXECUTIVE
            and lead.assigned_to != user
        ):
            raise PermissionDenied(
                "You can only schedule follow-ups for your assigned leads."
            )

        follow_up = serializer.save(
            assigned_to=assigned_to,
        )

        log_activity(
            entity_type=EntityType.FOLLOW_UP,
            entity_id=follow_up.id,
            action=ActionType.CREATED,
            performed_by=user,
            new_value={
                "lead_id": str(lead.id),
                "assigned_to": assigned_to.email,
                "follow_up_at": follow_up.follow_up_at.isoformat(),
                "purpose": follow_up.purpose,
            },
        )

    def perform_update(self, serializer):
        follow_up = serializer.instance
        old_purpose = follow_up.purpose
        old_follow_up_at = follow_up.follow_up_at

        follow_up = serializer.save()

        log_activity(
            entity_type=EntityType.FOLLOW_UP,
            entity_id=follow_up.id,
            action=ActionType.UPDATED,
            performed_by=self.request.user,
            old_value={
                "purpose": old_purpose,
                "follow_up_at": old_follow_up_at.isoformat() if old_follow_up_at else None,
            },
            new_value={
                "purpose": follow_up.purpose,
                "follow_up_at": follow_up.follow_up_at.isoformat() if follow_up.follow_up_at else None,
            },
        )

    def perform_destroy(self, instance):
        log_activity(
            entity_type=EntityType.FOLLOW_UP,
            entity_id=instance.id,
            action=ActionType.DELETED,
            performed_by=self.request.user,
            old_value={
                "lead_id": str(instance.lead_id),
                "purpose": instance.purpose,
            },
        )
        instance.delete()