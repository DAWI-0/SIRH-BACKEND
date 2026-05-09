from django.urls import path
from .views import PointageIoTListView

urlpatterns = [
    # Route pour React (GET) - AJOUTE BIEN LE SLASH À LA FIN
    path('pointages/', PointageIoTListView.as_view(), name='pointages-list'),
]