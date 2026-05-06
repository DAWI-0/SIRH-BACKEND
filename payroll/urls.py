from django.urls import path
from .views import ContratListCreateView, ContratDetailView, EvaluationListCreateView, FichePaieListCreateView

urlpatterns = [
    # Pour Créer (POST)
    path('contrats/', ContratListCreateView.as_view(), name='contrat-list'),
    
    # NOUVEAU : Pour Mettre à jour (PUT/PATCH) ou Supprimer un contrat spécifique
    path('contrats/<uuid:pk>/', ContratDetailView.as_view(), name='contrat-detail'),
    
    path('evaluations/', EvaluationListCreateView.as_view(), name='evaluation-list'),
    path('fiches/', FichePaieListCreateView.as_view(), name='fichepaie-list'),
]