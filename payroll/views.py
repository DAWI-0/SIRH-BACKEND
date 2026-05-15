from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from datetime import date
from accounts.models import Employe
from .models import PresenceManuelle, Contrat, Evaluation, FichePaie, Conge
from .serializers import ContratSerializer, EvaluationSerializer, FichePaieSerializer, CongeSerializer
# Assurez-vous d'importer PointageIoT si vous l'utilisez
# from attendance.models import PointageIoT

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

class TogglePresenceView(APIView):
    def get(self, request):
        mois = request.query_params.get('mois', 5)
        annee = request.query_params.get('annee', 2026)
        presences = PresenceManuelle.objects.filter(date_jour__year=annee, date_jour__month=mois)
        
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
        PresenceManuelle.objects.filter(date_jour__year=annee, date_jour__month=mois).delete()
        return Response({"message": "Toutes les présences ont été remises à zéro."})

class GenererPaieMensuelleView(APIView):
    def post(self, request):
        try:
            mois = int(request.data.get('mois', date.today().month))
            annee = int(request.data.get('annee', date.today().year))
        except (ValueError, TypeError):
            return Response({"error": "Mois ou année invalide."}, status=status.HTTP_400_BAD_REQUEST)

        employes = Employe.objects.filter(statut='ACTIF')
        fiches_creees = 0
        erreurs = []

        for employe in employes:
            salaire_base = Decimal('8000.00') # Salaire par défaut robuste

            # 1. Tenter de récupérer le vrai salaire de l'employé
            try:
                if hasattr(employe, 'salaire_mensuel') and employe.salaire_mensuel is not None:
                    salaire_base = Decimal(str(employe.salaire_mensuel))
                elif hasattr(employe, 'salaire') and employe.salaire is not None:
                    salaire_base = Decimal(str(employe.salaire))
                elif hasattr(employe, 'salaire_base') and employe.salaire_base is not None:
                    salaire_base = Decimal(str(employe.salaire_base))
                elif hasattr(employe, 'contrats') and employe.contrats.exists():
                     dernier_contrat = employe.contrats.last()
                     if dernier_contrat and dernier_contrat.salaire_mensuel is not None:
                         salaire_base = Decimal(str(dernier_contrat.salaire_mensuel))
            except InvalidOperation:
                erreurs.append(f"Erreur de conversion de salaire pour {employe.username}")
                continue # Passe à l'employé suivant si le salaire est cassé

            # 2. Définir le salaire journalier
            # On divise par 26 (jours ouvrables moyens) ou 30 selon la convention
            jours_ouvrables_moyens = Decimal('26.0')
            salaire_journalier = salaire_base / jours_ouvrables_moyens

            # 3. Récupérer les statuts de PresenceManuelle pour ce mois
            # Votre règle: ABSENT = Déduction, SUPP = Prime (Jours OFF travaillés)
            jours_absents = PresenceManuelle.objects.filter(
                employe=employe, 
                date_jour__year=annee, 
                date_jour__month=mois, 
                statut='ABSENT'
            ).count()

            jours_supp = PresenceManuelle.objects.filter(
                employe=employe, 
                date_jour__year=annee, 
                date_jour__month=mois, 
                statut='SUPP'
            ).count()

            # 4. Calculs financiers
            deductions = Decimal(jours_absents) * salaire_journalier
            primes = Decimal(jours_supp) * salaire_journalier # Optionnel: multiplier par 1.5 pour heures sup
            
            # Formule: Salaire de base - (jours non travaillés payés) + (jours bonus travaillés payés)
            net_a_payer = salaire_base - deductions + primes

            # 5. Créer ou Mettre à jour la Fiche de Paie
            try:
                FichePaie.objects.update_or_create(
                    employe=employe, 
                    periode_mois=mois, 
                    periode_annee=annee,
                    defaults={
                        'salaire_base': round(salaire_base, 2),
                        'deductions_absences': round(deductions, 2),
                        'primes_supp': round(primes, 2),
                        'net_a_payer': round(net_a_payer, 2)
                    }
                )
                fiches_creees += 1
            except Exception as e:
                erreurs.append(f"Erreur création fiche pour {employe.username}: {str(e)}")

        message = f"{fiches_creees} fiches de paie générées et calculées avec succès pour {mois}/{annee} !"
        if erreurs:
             message += f" Avec {len(erreurs)} erreurs (consulter les logs)."
             print("Erreurs Génération Paie:", erreurs)

        return Response({"message": message}, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
             mois = int(request.query_params.get('mois', date.today().month))
             annee = int(request.query_params.get('annee', date.today().year))
        except ValueError:
             return Response({"error": "Paramètres invalides."}, status=status.HTTP_400_BAD_REQUEST)
        
        fiches_supprimees, _ = FichePaie.objects.filter(periode_mois=mois, periode_annee=annee).delete()
        
        return Response({"message": f"Nettoyage réussi : {fiches_supprimees} fiches de paie ont été supprimées pour {mois}/{annee}."})

class CongeListCreateView(generics.ListCreateAPIView):
    queryset = Conge.objects.all()
    serializer_class = CongeSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', '') in ['RH', 'ADMIN']:
            return Conge.objects.all()
            
        try:
            employe_instance = Employe.objects.get(id=user.id)
            return Conge.objects.filter(employe=employe_instance)
        except Employe.DoesNotExist:
            return Conge.objects.none()

    def perform_create(self, serializer):
        employe_instance = Employe.objects.get(id=self.request.user.id)
        serializer.save(employe=employe_instance, statut='EN_ATTENTE')

class CongeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conge.objects.all()
    serializer_class = CongeSerializer
    # Assurez-vous que l'authentification est requise
    permission_classes = [IsAuthenticated] 

    def patch(self, request, *args, **kwargs):
        user = self.request.user
        
        # Vérification stricte du rôle
        if not (user.is_staff or getattr(user, 'role', '') in ['RH', 'ADMIN', 'ADMINISTRATEUR']):
            return Response({"error": "Seul un manager RH peut valider un congé."}, status=status.HTTP_403_FORBIDDEN)
            
        kwargs['partial'] = True 
        return super().update(request, *args, **kwargs)
class PointageVirtuelView(APIView):
    def post(self, request):
        try:
            employe = Employe.objects.get(id=request.user.id)
            aujourd_hui = date.today()

            PresenceManuelle.objects.update_or_create(
                employe=employe,
                date_jour=aujourd_hui,
                defaults={'statut': 'PRESENT'}
            )
            return Response({"message": f"Pointage virtuel réussi pour {aujourd_hui.strftime('%d/%m/%Y')} ✅"})
        except Employe.DoesNotExist:
            return Response({"error": "Profil employé introuvable."}, status=status.HTTP_404_NOT_FOUND)