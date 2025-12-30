"""
Permisos personalizados para el sistema.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permite acceso solo a usuarios administradores."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsReceptionOrAdmin(permissions.BasePermission):
    """Permite acceso a usuarios de recepción o administradores."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin or request.user.is_reception


class IsProfessionalOrAdmin(permissions.BasePermission):
    """Permite acceso a profesionales o administradores."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin or request.user.is_professional


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acceso al propietario del objeto o administradores.
    El objeto debe tener un campo 'user' o 'professional__user'.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True

        # Check for user field
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check for professional relationship
        if hasattr(obj, 'professional') and obj.professional:
            return obj.professional.user == request.user

        return False


class ReadOnlyForProfessional(permissions.BasePermission):
    """
    Profesionales solo pueden leer, admin/recepción pueden modificar.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin y recepción tienen acceso completo
        if request.user.is_admin or request.user.is_reception:
            return True

        # Profesionales solo lectura
        if request.user.is_professional:
            return request.method in permissions.SAFE_METHODS

        return False
