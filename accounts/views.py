from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status 

# 👇 NOUVEAU : Imports pour la vue des archives basée sur une fonction
from rest_framework.decorators import api_view, permission_classes

import requests

# Imports pour le Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Employe, ManagerRH, Administrateur, ArchiveEmploye
from .serializers import EmployeSerializer, ManagerRHSerializer
from .serializers import ArchiveEmployeSerializer
from .permissions import IsAdministrateur, IsAdminOrRH, IsChefDepartementOrRH
from organization.models import Departement


# --- VUES EXISTANTES ---

class CreateEmployeView(generics.CreateAPIView):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    permission_classes = [IsAdminOrRH]

class CreateManagerRHView(generics.CreateAPIView):
    queryset = ManagerRH.objects.all()
    serializer_class = ManagerRHSerializer
    permission_classes = [IsAdministrateur]

class EmployeListView(generics.ListAPIView):
    serializer_class = EmployeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # On accepte ADMIN, ADMINISTRATEUR ou RH
        if getattr(user, 'role', None) in ['ADMIN', 'ADMINISTRATEUR', 'RH'] or user.is_superuser:
            return Employe.objects.all()
        
        try:
            employe_connecte = Employe.objects.get(id=user.id)
            if hasattr(employe_connecte, 'departement_dirige'):
                return Employe.objects.filter(departement=employe_connecte.departement_dirige)
            return Employe.objects.filter(id=employe_connecte.id)
        except Employe.DoesNotExist:
            return Employe.objects.none()

class EmployeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employe.objects.all()
    serializer_class = EmployeSerializer
    permission_classes = [IsChefDepartementOrRH]

    def update(self, request, *args, **kwargs):
        nouveau_statut = request.data.get('statut')
        date_depart_frontend = request.data.get('date_depart')
        
        # Liste des statuts qui signifient que l'employé quitte l'entreprise
        statuts_de_depart = ['DEMISSIONNAIRE', 'LICENCIE']
        
        if nouveau_statut in statuts_de_depart:
            employe = self.get_object()
            import datetime
            final_date = date_depart_frontend if date_depart_frontend else datetime.date.today()
            
            # 1. ARCHIVAGE : On sauvegarde l'historique avec la raison du départ
            ArchiveEmploye.objects.create(
                username=employe.username,
                matricule=employe.matricule,
                poste_titre=employe.poste_titre,
                departement_nom=employe.departement.nom_departement if hasattr(employe, 'departement') and employe.departement else "Non assigné",
                statut_depart=nouveau_statut,
                matrice_competences_archive=employe.matrice_competences, # 👇 CORRECTION : Virgule ajoutée ici
                date_depart=final_date
            )

            # 2. AUTOMATISATION n8n : On précise le motif à n8n !
            webhook_url = 'http://127.0.0.1:5678/webhook-test/demission-alerte'
            payload = {
                "action": "DEPART_EMPLOYE",
                "motif_depart": nouveau_statut,
                "employe_nom": employe.username,
                "poste_a_pourvoir": employe.poste_titre,
                "competences_cles": employe.matrice_competences
            }
            try:
                requests.post(webhook_url, json=payload, timeout=2)
                print(f"ALERTE n8n ENVOYÉE : Départ de {employe.username} ({nouveau_statut})")
            except Exception as e:
                print(f"Erreur Webhook n8n : {e}")

            # 3. SUPPRESSION : On supprime l'utilisateur de la base active (ce qui bloque aussi sa connexion)
            employe.delete()
            
            return Response(
                {"message": f"Dossier traité. L'employé a été archivé pour motif : {nouveau_statut}."}, 
                status=status.HTTP_200_OK
            )
        else:
            # Si ce n'est pas un départ, on met simplement à jour
            return super().update(request, *args, **kwargs)


# --- NOUVELLE VUE : RÉCUPÉRATION DES ARCHIVES ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_archives(request):
    # Récupère le motif depuis l'URL envoyé par React (ex: ?motif=Licenciement)
    motif = request.GET.get('motif', '').upper()
    
    # Mapping pour faire correspondre les mots du frontend avec votre BDD exacte
    statut_mapping = {
        'LICENCIEMENT': 'LICENCIE',
        'DÉMISSION': 'DEMISSIONNAIRE',
        'DEMISSION': 'DEMISSIONNAIRE'
    }
    
    if motif in statut_mapping:
        # On filtre par le vrai statut de la base de données (ex: 'LICENCIE')
        archives = ArchiveEmploye.objects.filter(statut_depart=statut_mapping[motif])
    elif motif:
        # Sécurité supplémentaire au cas où
        archives = ArchiveEmploye.objects.filter(statut_depart__icontains=motif)
    else:
        # Si aucun motif n'est précisé, on renvoie tout
        archives = ArchiveEmploye.objects.all()
        
    serializer = ArchiveEmployeSerializer(archives, many=True)
    return Response(serializer.data)


# --- PERSONNALISATION DU TOKEN JWT SÉCURISÉE ---

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # On injecte le nom d'utilisateur
        token['username'] = user.username
        
        # 1. Gestion du rôle
        if user.is_superuser:
            token['role'] = 'ADMINISTRATEUR'
        else:
            token['role'] = getattr(user, 'role', 'EMPLOYE') 
        
        # 2. Gestion du statut de Chef
        token['is_chef'] = False
        if Departement.objects.filter(manager=user).exists():
            token['is_chef'] = True
            
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer