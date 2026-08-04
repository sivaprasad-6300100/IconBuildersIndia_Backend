from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin users can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsClient(BasePermission):
    """Only client users can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'client'
        )


class IsContractor(BasePermission):
    """Only contractor users can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'contractor'
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin can do anything, others can only read"""
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsAdminOrClient(BasePermission):
    """Admin or Client can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'client')
        )


class IsAdminOrContractor(BasePermission):
    """Admin or Contractor can access"""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'contractor')
        )