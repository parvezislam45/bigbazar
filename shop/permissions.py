
from rest_framework.permissions import BasePermission

class IsVendorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        print(f"Authenticated: {request.user.is_authenticated}, Role: {getattr(request.user, 'role', None)}")
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['vendor', 'admin']
        )
