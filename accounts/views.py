from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Employe, ManagerRH
from .serializers import EmployeSerializer, ManagerRHSerializer
from .permissions import IsAdministrateur, IsAdminOrRH

class CreateEmployeView(generics.CreateAPIView):
    """
    Endpoint for creating an Employe. 
    Accessible by both ADMIN and RH.
    """
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    permission_classes = [IsAdminOrRH]

class CreateManagerRHView(generics.CreateAPIView):
    """
    Endpoint for creating a Manager RH.
    Accessible ONLY by ADMIN.
    """
    queryset = ManagerRH.objects.all()
    serializer_class = ManagerRHSerializer
    permission_classes = [IsAdministrateur]