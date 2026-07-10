from rest_framework.permissions import BasePermission

from core.choices import UserRole


class RolePermission(BasePermission):
    """
    Base permission class for role-based access.
    """

    allowed_roles = ()

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )


class IsAdmin(RolePermission):
    allowed_roles = (
        UserRole.ADMIN,
    )


class IsSalesManager(RolePermission):
    allowed_roles = (
        UserRole.SALES_MANAGER,
    )


class IsSalesExecutive(RolePermission):
    allowed_roles = (
        UserRole.SALES_EXECUTIVE,
    )


class IsAdminOrManager(RolePermission):
    allowed_roles = (
        UserRole.ADMIN,
        UserRole.SALES_MANAGER,
    )


class IsStaff(RolePermission):
    allowed_roles = (
        UserRole.ADMIN,
        UserRole.SALES_MANAGER,
        UserRole.SALES_EXECUTIVE,
    )