# permissions.py
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users
    """
    def has_permission(self, request, view):
        # Admin or superuser can access
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role == 'admin'
        )

class IsManagerUser(permissions.BasePermission):
    """
    Custom permission to only allow managers
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role in ['admin', 'manager']
        )

class IsStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow staff members
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.role in ['admin', 'manager', 'staff']
        )