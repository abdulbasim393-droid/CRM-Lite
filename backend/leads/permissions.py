from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.choices import UserRole


class LeadPermission(BasePermission):
    """
    Role-based and object-level permissions for Lead operations.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin and Sales Manager can access every lead.
        if user.role in (
            UserRole.ADMIN,
            UserRole.SALES_MANAGER,
        ):
            return True

        # Sales Executive can only access their own assigned leads.
        if user.role == UserRole.SALES_EXECUTIVE:
            return obj.assigned_to == user

        return False