from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Employe, ManagerRH
from .serializers import EmployeSerializer, ManagerRHSerializer
from .permissions import IsAdministrateur, IsAdminOrRH

class CreateEmployeView(generics.CreateAPIView):
    
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    permission_classes = [IsAdminOrRH]

class CreateManagerRHView(generics.CreateAPIView):
   
    queryset = ManagerRH.objects.all()
    serializer_class = ManagerRHSerializer
    permission_classes = [IsAdministrateur]
   
class EmployeListView(generics.ListAPIView):
    
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    permission_classes = [IsAdminOrRH]

class EmployeDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    permission_classes = [IsAdminOrRH]