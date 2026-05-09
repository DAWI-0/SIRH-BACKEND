from django.urls import path
from .views import (
    ContratListCreateView, ContratDetailView,
    EvaluationListCreateView, 
    FichePaieListCreateView, GenererPaieMensuelleView,
    CongeListCreateView, CongeDetailView,TogglePresenceView,PointageVirtuelView  # 👈 N'oublie pas cet import !

)

urlpatterns = [
    path('contrats/', ContratListCreateView.as_view(), name='contrat-list'),
    path('contrats/<uuid:pk>/', ContratDetailView.as_view(), name='contrat-detail'),
    
    path('evaluations/', EvaluationListCreateView.as_view(), name='evaluation-list'),
    
    path('fiches/', FichePaieListCreateView.as_view(), name='fiche-list'),
    path('generer-paie/', GenererPaieMensuelleView.as_view(), name='generer-paie'),
    

    # 👇 LES DEUX NOUVELLES ROUTES POUR LES CONGÉS SONT ICI 👇
    path('conges/', CongeListCreateView.as_view(), name='conge-list'),
    path('conges/<uuid:pk>/', CongeDetailView.as_view(), name='conge-detail'),
    path('presences-manuelles/toggle/', TogglePresenceView.as_view(), name='toggle-presence'),
    path('pointage-virtuel/', PointageVirtuelView.as_view(), name='pointage-virtuel')
]