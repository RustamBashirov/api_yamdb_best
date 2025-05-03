from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Права доступа администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class ReadOnly(BasePermission):
    """Права доступа администратора или только чтение."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthorOrAdminOrModeratorOrReadOnly(BasePermission):
    """
    Права доступа автора, администратора, модератора
    или только чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )
