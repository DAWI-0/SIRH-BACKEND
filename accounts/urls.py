from django.urls import path
from .views import CreateEmployeView, CreateManagerRHView

urlpatterns = [
    path('create-employe/', CreateEmployeView.as_view(), name='create-employe'),
    path('create-rh/', CreateManagerRHView.as_view(), name='create-rh'),
]