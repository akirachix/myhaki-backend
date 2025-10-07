from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows Admins (role='admin') full access (list, create). Others get read-only access.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return request.method in permissions.SAFE_METHODS

class IsAdminOrIsAssignedLawyer(permissions.BasePermission):
    """
    Allows:
    1. Admins (role='admin') full access.
    2. The Assigned Lawyer to update their specific CaseAssignment object.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if hasattr(obj.lawyer, 'user'):
                return obj.lawyer.user == request.user
            return False 
        
        return False
