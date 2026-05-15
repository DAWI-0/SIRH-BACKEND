from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import datetime
import requests

# Imports pour le Token JWT
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Employe, ManagerRH, Administrateur, ArchiveEmploye
from .serializers import EmployeSerializer, ManagerRHSerializer, ArchiveEmployeSerializer
from .permissions import IsAdministrateur, IsAdminOrRH, IsChefDepartementOrRH
from organization.models import Departement
from payroll.models import PresenceManuelle, Conge # 👈 Import de Conge ajouté ici

# ==========================================
# 1. GESTION DES EMPLOYÉS (CRUD)
# ==========================================

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
        
        statuts_de_depart = ['DEMISSIONNAIRE', 'LICENCIE']
        
        if nouveau_statut in statuts_de_depart:
            employe = self.get_object()
            final_date = date_depart_frontend if date_depart_frontend else datetime.date.today()
            
            # 1. ARCHIVAGE
            ArchiveEmploye.objects.create(
                username=employe.username,
                matricule=employe.matricule,
                poste_titre=employe.poste_titre,
                departement_nom=employe.departement.nom_departement if hasattr(employe, 'departement') and employe.departement else "Non assigné",
                statut_depart=nouveau_statut,
                matrice_competences_archive=employe.matrice_competences,
                date_depart=final_date
            )

            # 2. AUTOMATISATION n8n
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
            except Exception as e:
                print(f"Erreur Webhook n8n : {e}")

            # 3. SUPPRESSION
            employe.delete()
            
            return Response(
                {"message": f"Dossier traité. L'employé a été archivé ({nouveau_statut})."}, 
                status=status.HTTP_200_OK
            )
        else:
            return super().update(request, *args, **kwargs)

# ==========================================
# 2. ARCHIVES & STATISTIQUES (DASHBOARD)
# ==========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_archives(request):
    motif = request.GET.get('motif', '').upper()
    statut_mapping = {
        'LICENCIEMENT': 'LICENCIE',
        'DÉMISSION': 'DEMISSIONNAIRE',
        'DEMISSION': 'DEMISSIONNAIRE'
    }
    
    if motif in statut_mapping:
        archives = ArchiveEmploye.objects.filter(statut_depart=statut_mapping[motif])
    elif motif:
        archives = ArchiveEmploye.objects.filter(statut_depart__icontains=motif)
    else:
        archives = ArchiveEmploye.objects.all()
        
    serializer = ArchiveEmployeSerializer(archives, many=True)
    return Response(serializer.data)

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if getattr(user, 'role', '') not in ['ADMIN', 'ADMINISTRATEUR', 'RH'] and not user.is_superuser:
            return Response({"error": "Accès refusé."}, status=status.HTTP_403_FORBIDDEN)

        aujourd_hui = timezone.localtime().date()
        debut_mois = aujourd_hui.replace(day=1)

        # --- 1. KPIs ---
        actifs = Employe.objects.filter(statut='ACTIF')
        total_actifs = actifs.count()
        nouveaux_ce_mois = actifs.filter(date_joined__gte=debut_mois).count()
        masse_salariale = actifs.aggregate(total=Sum('salaire'))['total'] or 0
        presents_jour = PresenceManuelle.objects.filter(date_jour=aujourd_hui, statut='PRESENT').count()
        absents_jour = PresenceManuelle.objects.filter(date_jour=aujourd_hui, statut='ABSENT').count()
        taux_presence = int((presents_jour / total_actifs * 100)) if total_actifs > 0 else 0

        # --- 2. GRAPH: DÉPARTEMENTS ---
        dept_data = []
        departements = Departement.objects.annotate(effectif=Count('employes', filter=Q(employes__statut='ACTIF')))
        for d in departements:
            if d.effectif > 0:
                dept_data.append({"name": d.nom_departement, "effectif": d.effectif})

        # --- 3. GRAPH: CONTRATS ---
        contrats_counts = actifs.values('type_contrat').annotate(value=Count('id'))
        couleurs = {'CDI': '#fde047', 'CDD': '#c084fc', 'STAGE': '#4ade80', 'FREELANCE': '#f87171'}
        contrat_data = [{"name": c['type_contrat'], "value": c['value'], "color": couleurs.get(c['type_contrat'], '#9ca3af')} for c in contrats_counts]

        # --- 4. GRAPH: PRÉSENCES SEMAINE ---
        attendance_data = []
        jours_fr = {'Mon':'Lun', 'Tue':'Mar', 'Wed':'Mer', 'Thu':'Jeu', 'Fri':'Ven', 'Sat':'Sam', 'Sun':'Dim'}
        for i in range(4, -1, -1):
            jour = aujourd_hui - timedelta(days=i)
            p = PresenceManuelle.objects.filter(date_jour=jour, statut='PRESENT').count()
            a = PresenceManuelle.objects.filter(date_jour=jour, statut='ABSENT').count()
            attendance_data.append({
                "day": jours_fr.get(jour.strftime('%a'), jour.strftime('%a')),
                "presents": p, "absents": a
            })

        # --- 5. ACTIONS RAPIDES: CONGÉS EN ATTENTE ---
        conges_en_attente = Conge.objects.filter(statut='EN_ATTENTE').select_related('employe')
        conges_list = [{
            "id": str(c.id),
            "employe_nom": c.employe.username,
            "date_debut": c.date_debut,
            "date_fin": c.date_fin
        } for c in conges_en_attente]

        return Response({
            "kpis": {
                "total_actifs": total_actifs,
                "nouveaux_ce_mois": nouveaux_ce_mois,
                "masse_salariale": masse_salariale,
                "taux_presence": taux_presence,
                "absents_jour": absents_jour
            },
            "charts": {
                "departements": dept_data,
                "contrats": contrat_data,
                "presences_semaine": attendance_data
            },
            "conges_attente": conges_list
        })

# ==========================================
# 3. AUTHENTIFICATION & TOKENS
# ==========================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        if user.is_superuser:
            token['role'] = 'ADMINISTRATEUR'
        else:
            token['role'] = getattr(user, 'role', 'EMPLOYE') 
        
        token['is_chef'] = Departement.objects.filter(manager=user).exists()
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer