"""
Custom DRF permission classes.
"""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allow access only to users whose role == 'admin'.
    Note: this is different from is_staff / is_superuser.
    """
    message = "Access restricted to administrators only."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission — allow owners to access their own objects
    and admins to access everything.
    """
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        # obj is expected to have a user FK or be a User instance
        owner = getattr(obj, "user", obj)
        return owner == request.user
