from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from accounts.models import UserRole
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = Customer.objects.select_related(
            "lead",
            "created_by",
        )

        if user.role in (
            UserRole.ADMIN,
            UserRole.SALES_MANAGER,
        ):
            return queryset

        return queryset.filter(
            lead__assigned_to=user,
        )