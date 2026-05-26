from rest_framework import permissions

class IsBursar(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'bursar'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsPrincipal(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'principal'

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'parent'

class IsStaffOrAdmin(permissions.BasePermission):
    """For bursar, admin, principal, teacher – any staff role"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['bursar', 'admin', 'principal', 'teacher']