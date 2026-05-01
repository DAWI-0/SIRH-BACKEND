from django.urls import path
from .views import IoTPontageView

urlpatterns = [
    path('log/', IoTPontageView.as_view(), name='iot_log'),
]