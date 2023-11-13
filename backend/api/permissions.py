from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAdminUser)


class AuthorOrStaffOrReadOnly(BasePermission):
    """Если не админ или не автор, то только чтение"""

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)


class AdminOrReadOnly(IsAdminUser):
    """Если не админ, то только чтение"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
        )
