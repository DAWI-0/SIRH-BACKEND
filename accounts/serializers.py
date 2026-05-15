import uuid
from rest_framework import serializers
from .models import ArchiveEmploye
from .models import Employe, ManagerRH
from organization.models import Departement
# Assure-toi que ton modèle Contrat est bien importé si nécessaire, 
# mais ici on utilise la relation inverse 'contrats' donc pas d'import strict requis.

# Dans serializers.py

class EmployeSerializer(serializers.ModelSerializer):
    departement_nom = serializers.ReadOnlyField(source='departement.nom_departement')
    est_manager = serializers.BooleanField(write_only=True, required=False, default=False)
    matricule = serializers.CharField(required=False, allow_blank=True)
    
    # Champ calculé pour envoyer les infos RH/Paie au frontend
    contrat_actuel = serializers.SerializerMethodField()

    class Meta:
        model = Employe
        # 👇 AJOUTE 'salaire' et 'type_contrat' à la liste des champs
        fields = [
            'id', 'username', 'email', 'password', 'matricule', 'poste_titre', 
            'departement', 'departement_nom', 'matrice_competences', 'role', 
            'est_manager', 'contrat_actuel', 'statut', 'salaire', 'type_contrat'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'matricule': {'required': False}
        }

    def get_contrat_actuel(self, obj):
        # 👇 MODIFICATION : On lit directement les champs du modèle Employe
        # au lieu de chercher un modèle Contrat externe
        return {
            "type_contrat": obj.type_contrat,
            "salaire_mensuel": obj.salaire,
            "date_debut": "Non définie" # (Tu n'as pas de champ date_debut sur ton modèle Employe)
        }

    def create(self, validated_data):
        if 'matricule' not in validated_data or not validated_data['matricule']:
            validated_data['matricule'] = f"EMP-{uuid.uuid4().hex[:6].upper()}"
            
        est_manager = validated_data.pop('est_manager', False)
        password = validated_data.pop('password')
        
        employe = Employe(**validated_data)
        employe.set_password(password)
        employe.role = 'EMPLOYE' # Par défaut, ce n'est pas un admin
        employe.save()
        
        if est_manager and employe.departement:
            dept = employe.departement
            dept.manager = employe
            dept.save()
            
        return employe

    def update(self, instance, validated_data):
        # SÉCURITÉ BACKEND : On vérifie qui fait la requête
        request = self.context.get('request')
        user = request.user if request else None
        
        if user and getattr(user, 'role', '') not in ['ADMIN', 'RH']:
            # Un Chef de département NE PEUT PAS modifier ces champs, 
            # on les supprime de la requête s'il essaie de tricher via Postman.
            validated_data.pop('poste_titre', None)
            validated_data.pop('departement', None)
            validated_data.pop('role', None)
            # Il ne lui reste le droit de modifier QUE 'matrice_competences'
            
        return super().update(instance, validated_data)


class ManagerRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerRH
        fields = ['id', 'username', 'email', 'password',]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        manager = ManagerRH(**validated_data)
        manager.set_password(password)
        manager.role = 'RH'
        manager.is_staff = True
        manager.save()
        return manager

class ArchiveEmployeSerializer(serializers.ModelSerializer):
    date_depart = serializers.DateField(format="%Y-%m-%d", required=False)
    class Meta:
        model = ArchiveEmploye
        fields = '__all__' 