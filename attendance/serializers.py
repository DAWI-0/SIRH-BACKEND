from rest_framework import serializers
from django.utils import timezone
from .models import PointageIoT
from accounts.models import Employe

class PointageIoTSerializer(serializers.ModelSerializer):
    employe = serializers.SlugRelatedField(
        queryset=Employe.objects.all(),
        slug_field='matricule'
    )
    
    employe_nom = serializers.ReadOnlyField(source='employe.username')
    matricule_display = serializers.ReadOnlyField(source='employe.matricule')
    
    # 👇 LE NOUVEAU CHAMP CALCULÉ PAR LE BACKEND 👇
    is_late = serializers.SerializerMethodField()

    class Meta:
        model = PointageIoT
        fields = [
            'id', 'employe', 'employe_nom', 'matricule_display', 
            'type_pointage', 'timestamp', 'id_capteur', 'est_justifie', 
            'is_late' # <-- Ne pas oublier de l'ajouter ici !
        ]

    # La fonction qui calcule "is_late"
    def get_is_late(self, obj):
        if obj.type_pointage != 'ENTREE':
            return False
            
        # On convertit le timestamp en heure locale du serveur
        heure_locale = timezone.localtime(obj.timestamp)
        
        # Retard si strictement supérieur à 09h00
        return heure_locale.hour > 9 or (heure_locale.hour == 9 and heure_locale.minute > 0)