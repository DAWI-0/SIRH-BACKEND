from django.urls import path
from . import views

urlpatterns = [
    # Récupérer la liste des conversations (1 pour l'employé, plusieurs pour le RH)
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    
    # Récupérer l'historique des messages d'une conversation spécifique
    path('conversations/<int:conv_id>/messages/', views.MessageListView.as_view(), name='message-list'),
    
    # Envoyer un message (déclenche aussi l'envoi WebSocket)
    path('messages/send/', views.SendMessageView.as_view(), name='message-send'),
]