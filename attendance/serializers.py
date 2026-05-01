from rest_framework import serializers
from .models import PointageIoT
from accounts.models import Employe

class PointageIoTSerializer(serializers.ModelSerializer):
    matricule = serializers.CharField(write_only=True)

    class Meta:
        model = PointageIoT
        fields = ['matricule', 'type_pointage', 'timestamp', 'id_capteur', 'est_justifie']
        # On peut laisser est_justifie à False par défaut comme dans ton modèle

    def create(self, validated_data):
        matricule = validated_data.pop('matricule')
        try:
            employe = Employe.objects.get(matricule=matricule) # Adapte "matricule=" selon comment tu l'as nommé dans accounts/models.py
        except Employe.DoesNotExist:
            raise serializers.ValidationError({"matricule": "Cet employé n'existe pas."})
            
        # 3. On crée le pointage avec le bon employé
        pointage = PointageIoT.objects.create(employe=employe, **validated_data)
        return pointage
        