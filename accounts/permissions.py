from rest_framework.permissions import BasePermission

class IsAdministrateur(BasePermission):
    """ Allows access only to users with the ADMIN role. """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')

class IsManagerRH(BasePermission):
    """ Allows access only to users with the RH role. """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'RH')

class IsAdminOrRH(BasePermission):
    """ Allows access to both ADMIN and RH roles (for creating Employes). """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'RH'])