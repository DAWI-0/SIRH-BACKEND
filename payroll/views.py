from rest_framework import generics
from .models import Contrat, Evaluation, FichePaie
from .serializers import ContratSerializer, EvaluationSerializer, FichePaieSerializer

class ContratListCreateView(generics.ListCreateAPIView):
    queryset = Contrat.objects.all()
    serializer_class = ContratSerializer
    permission_classes = []
    authentication_classes = []

# 👇 NOUVELLE VUE AJOUTÉE POUR LA MODIFICATION 👇
class ContratDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contrat.objects.all()
    serializer_class = ContratSerializer
    permission_classes = []
    authentication_classes = []

class EvaluationListCreateView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = []
    authentication_classes = []

class FichePaieListCreateView(generics.ListCreateAPIView):
    queryset = FichePaie.objects.all()
    serializer_class = FichePaieSerializer
    permission_classes = []
    authentication_classes = []