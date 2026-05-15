from django.urls import path
from .views import (
    CreateEmployeView, 
    CreateManagerRHView, 
    EmployeListView, 
    EmployeDetailView,
    get_archives # 👇 NOUVEAU : Import de la fonction
)

urlpatterns = [
    # Création (Create)
    path('create-employe/', CreateEmployeView.as_view(), name='create-employe'),
    path('create-rh/', CreateManagerRHView.as_view(), name='create-rh'),
    
    # Lecture globale (Read All)
    path('employes/', EmployeListView.as_view(), name='liste-employes'),
    
    # Lecture spécifique, Modification et Suppression (Read, Update, Delete)
    # L'URL attend l'ID (UUID) de l'employé
    path('employes/<uuid:pk>/', EmployeDetailView.as_view(), name='detail-employe'),

    # 👇 CORRECTION ICI : Pas de .as_view() car get_archives est une fonction
    path('archives/', get_archives, name='get_archives'),
]