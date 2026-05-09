from rest_framework import serializers
from .models import Contrat, Evaluation, FichePaie, Conge

class ContratSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrat
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

class FichePaieSerializer(serializers.ModelSerializer):
    employe = serializers.CharField(source='employe.username', read_only=True)
    
    class Meta:
        model = FichePaie
        fields = '__all__'

class CongeSerializer(serializers.ModelSerializer):
    employe_nom = serializers.ReadOnlyField(source='employe.username')
    
    class Meta:
        model = Conge
        fields = '__all__'
        # 👇 NOUVEAU : On empêche l'utilisateur de modifier ça !
        read_only_fields = ['employe']