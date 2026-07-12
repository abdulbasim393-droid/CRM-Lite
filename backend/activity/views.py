from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.choices import UserRole

from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogViewSet(ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_fields = (
        "entity_type",
        "action",
        "performed_by",
    )

    search_fields = (
        "entity_type",
        "action",
    )

    ordering_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def get_queryset(self):
        user = self.request.user

        queryset = ActivityLog.objects.select_related(
            "performed_by",
        )

        if user.role in (
            UserRole.ADMIN,
            UserRole.SALES_MANAGER,
        ):
            return queryset

        return queryset.filter(
            performed_by=user,
        )