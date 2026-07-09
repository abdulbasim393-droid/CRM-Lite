from rest_framework.permissions import BasePermission


class LeadPermission(BasePermission):
    """
    Role-based permissions for Lead operations.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated