from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from datetime import date
from accounts.models import Employe
from .models import PresenceManuelle 
# Tes modèles actuels
from .models import Contrat, Evaluation, FichePaie, Conge
from .serializers import ContratSerializer, EvaluationSerializer, FichePaieSerializer, CongeSerializer

# Les modèles externes nécessaires pour le calcul de paie
from accounts.models import Employe
from attendance.models import PointageIoT

class ContratListCreateView(generics.ListCreateAPIView):
    queryset = Contrat.objects.all()
    serializer_class = ContratSerializer
    permission_classes = []
    authentication_classes = []

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

from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FichePaie, PresenceManuelle
from accounts.models import Employe

class TogglePresenceView(APIView):
    # NOUVEAU : Permet à React de récupérer les bulles déjà sauvegardées
    def get(self, request):
        mois = request.query_params.get('mois', 5)
        annee = request.query_params.get('annee', 2026)
        presences = PresenceManuelle.objects.filter(date_jour__year=annee, date_jour__month=mois)
        
        # On crée un dictionnaire parfait pour React : {"ID_EMPLOYE-12": "ABSENT"}
        data = {f"{p.employe_id}-{p.date_jour.day}": p.statut for p in presences}
        return Response(data)

    def post(self, request):
        employe_id = request.data.get('employe_id')
        date_jour = request.data.get('date_jour')
        nouveau_statut = request.data.get('statut')

        presence, created = PresenceManuelle.objects.update_or_create(
            employe_id=employe_id,
            date_jour=date_jour,
            defaults={'statut': nouveau_statut}
        )
        return Response({"message": "Statut mis à jour", "statut": presence.statut})
    def delete(self, request):
        mois = request.query_params.get('mois', 5)
        annee = request.query_params.get('annee', 2026)
        # On supprime toutes les bulles de ce mois-ci
        PresenceManuelle.objects.filter(date_jour__year=annee, date_jour__month=mois).delete()
        return Response({"message": "Toutes les présences ont été remises à zéro."})

class GenererPaieMensuelleView(APIView):
    def post(self, request):
        mois = request.data.get('mois', 5)
        annee = request.data.get('annee', 2026)
        employes = Employe.objects.filter(statut='ACTIF')
        fiches_creees = 0

        for employe in employes:
            salaire_base = Decimal('8000.00') 
            
            if hasattr(employe, 'salaire_mensuel') and employe.salaire_mensuel:
                salaire_base = Decimal(str(employe.salaire_mensuel))
            elif hasattr(employe, 'salaire') and employe.salaire:
                salaire_base = Decimal(str(employe.salaire))
            elif hasattr(employe, 'salaire_base') and employe.salaire_base:
                salaire_base = Decimal(str(employe.salaire_base))
            elif hasattr(employe, 'contrats') and employe.contrats.exists():
                salaire_base = Decimal(str(employe.contrats.last().salaire_mensuel))

            salaire_journalier = salaire_base / Decimal('26.0')

            jours_absents = PresenceManuelle.objects.filter(employe=employe, date_jour__year=annee, date_jour__month=mois, statut='ABSENT').count()
            jours_supp = PresenceManuelle.objects.filter(employe=employe, date_jour__year=annee, date_jour__month=mois, statut='SUPP').count()

            deductions = Decimal(jours_absents) * salaire_journalier
            primes = Decimal(jours_supp) * salaire_journalier
            net_a_payer = salaire_base - deductions + primes

            FichePaie.objects.update_or_create(
                employe=employe, periode_mois=mois, periode_annee=annee,
                defaults={
                    'salaire_base': round(salaire_base, 2),
                    'deductions_absences': round(deductions, 2),
                    'primes_supp': round(primes, 2),
                    'net_a_payer': round(net_a_payer, 2)
                }
            )
            fiches_creees += 1

        # 👇 C'EST CETTE LIGNE QUI AVAIT DISPARU ! 👇
        return Response({"message": f"{fiches_creees} fiches de paie générées et calculées avec succès pour {mois}/{annee} !"})

    def delete(self, request):
        mois = request.query_params.get('mois', 5)
        annee = request.query_params.get('annee', 2026)
        
        # On supprime toutes les fiches de paie de ce mois/année
        fiches_supprimees, _ = FichePaie.objects.filter(periode_mois=mois, periode_annee=annee).delete()
        
        return Response({"message": f"Nettoyage réussi : {fiches_supprimees} fiches de paie ont été supprimées pour {mois}/{annee}."})
class CongeListCreateView(generics.ListCreateAPIView):
    queryset = Conge.objects.all()
    serializer_class = CongeSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Si c'est un RH ou un Admin, on montre tout
        if user.is_staff or getattr(user, 'role', '') in ['RH', 'ADMIN']:
            return Conge.objects.all()
            
        # Sinon, on cherche son profil Employé et on filtre
        try:
            employe_instance = Employe.objects.get(id=user.id)
            return Conge.objects.filter(employe=employe_instance)
        except Employe.DoesNotExist:
            return Conge.objects.none()

    def perform_create(self, serializer):
        employe_instance = Employe.objects.get(id=self.request.user.id)
        # 👇 On force le statut par défaut ici !
        serializer.save(employe=employe_instance, statut='EN_ATTENTE')
class CongeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conge.objects.all()
    serializer_class = CongeSerializer

    # On s'assure que n'importe qui peut pas valider ses propres congés
    def update(self, request, *args, **kwargs):
        # On vérifie si l'utilisateur est RH ou Admin
        user = self.request.user
        if not (user.is_staff or getattr(user, 'role', '') in ['RH', 'ADMIN']):
            return Response({"error": "Seul un manager RH peut valider un congé."}, status=status.HTTP_403_FORBIDDEN)
            
        # PATCH au lieu de PUT pour ne modifier QUE le statut
        kwargs['partial'] = True 
        return super().update(request, *args, **kwargs)
class PointageVirtuelView(APIView):
    def post(self, request):
        try:
            # On récupère l'employé connecté
            employe = Employe.objects.get(id=request.user.id)
            aujourd_hui = date.today()

            # On met à jour ou on crée la bulle verte pour aujourd'hui
            PresenceManuelle.objects.update_or_create(
                employe=employe,
                date_jour=aujourd_hui,
                defaults={'statut': 'PRESENT'}
            )
            return Response({"message": f"Pointage virtuel réussi pour {aujourd_hui.strftime('%d/%m/%Y')} ✅"})
        except Employe.DoesNotExist:
            return Response({"error": "Profil employé introuvable."}, status=404)        