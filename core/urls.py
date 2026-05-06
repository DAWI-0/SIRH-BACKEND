from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from accounts.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Tes applications existantes
    path('api/accounts/', include('accounts.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/organization/', include('organization.urls')),
    
    # LA LIGNE MAGIQUE QUI MANQUAIT 
    path('api/payroll/', include('payroll.urls')), 
]