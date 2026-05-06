from django.contrib import admin
from .models import Employe, ManagerRH, Administrateur, ArchiveEmploye, Utilisateur
from django.utils.safestring import mark_safe

# 1. On crée des filtres personnalisés pour l'affichage Admin
class EmployeAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='EMPLOYE')

class ManagerRHAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role='RH')

class AdministrateurAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(role__in=['ADMINISTRATEUR', 'ADMIN'])


class ArchiveEmployeAdmin(admin.ModelAdmin):
    # On utilise directement 'colored_name' ici au lieu de le définir deux fois
    list_display = ('colored_name', 'matricule', 'departement_nom', 'date_depart', 'statut_depart')
    list_filter = ('statut_depart', 'date_depart')
    search_fields = ('username', 'matricule', 'departement_nom')
    readonly_fields = ('date_depart', 'matrice_competences_archive')
    date_hierarchy = 'date_depart'
    
    # On empêche les utilisateurs normaux de supprimer/modifier les archives
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    
    # On met en gras les démissions
    def colored_name(self, obj):
        if obj.statut_depart == 'DEMISSIONNAIRE':
            return mark_safe(f'<span style="color: red;">{obj.username}</span>')
        return obj.username
    colored_name.short_description = 'Nom de l\'employé'


# 2. On enregistre les modèles avec leurs filtres respectifs
admin.site.register(Employe, EmployeAdmin)
admin.site.register(ManagerRH, ManagerRHAdmin)
admin.site.register(Administrateur, AdministrateurAdmin)
admin.site.register(ArchiveEmploye, ArchiveEmployeAdmin)
admin.site.register(Utilisateur)
