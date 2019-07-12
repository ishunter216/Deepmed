from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Allows to edit only to staff users.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff


class IsStaff(permissions.BasePermission):
    """
    Allows to edit and see only to staff users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
