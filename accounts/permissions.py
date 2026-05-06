from rest_framework.permissions import BasePermission
from .models import Employe

class IsAdministrateur(BasePermission):
    def has_permission(self, request, view): # <-- AJOUT DE 'view'
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')

class IsManagerRH(BasePermission):
    def has_permission(self, request, view): # <-- AJOUT DE 'view'
        return bool(request.user and request.user.is_authenticated and request.user.role == 'RH')

class IsAdminOrRH(BasePermission):
    def has_permission(self, request, view): # <-- AJOUT DE 'view'
        return bool(request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'RH'])

class IsChefDepartementOrRH(BasePermission):
    def has_object_permission(self, request, view, obj): # <-- AJOUT DE 'view'
        # Admin et RH ont tous les droits
        if request.user.role in ['ADMIN', 'RH']:
            return True
            
        # Vérification pour le Chef de département
        try:
            employe_connecte = Employe.objects.get(id=request.user.id)
            if obj.departement and getattr(obj.departement, 'manager', None) == employe_connecte:
                return True
        except Employe.DoesNotExist:
            pass
            
        return False