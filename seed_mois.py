import os
import django
from django.utils import timezone
import random
from datetime import timedelta

# ⚠️ N'oublie pas de mettre le bon nom de ton projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nom_de_ton_projet.settings')
django.setup()

from accounts.models import Employe
from attendance.models import PointageIoT
from payroll.models import FichePaie

def simuler_mois_complet():
    print("🧹 Nettoyage des anciens pointages et fiches de paie...")
    PointageIoT.objects.all().delete()
    FichePaie.objects.all().delete()

    employes = Employe.objects.filter(statut='ACTIF')
    maintenant = timezone.localtime()
    
    print(f"⏳ Génération de 26 jours de pointages pour {employes.count()} employés...")
    
    # On va simuler les 26 derniers jours de travail
    for i in range(26):
        date_jour = maintenant - timedelta(days=(26 - i))
        
        for employe in employes:
            # On donne à chacun 95% de chance d'être venu travailler (donc 5% d'absences)
            est_present = random.random() > 0.05 
            
            if est_present:
                PointageIoT.objects.create(
                    employe=employe,
                    type_pointage='ENTREE',
                    # On met l'heure d'arrivée à 08h45 pour tout le monde dans ce test
                    timestamp=date_jour.replace(hour=8, minute=45), 
                    id_capteur='SIMULATION_MOIS',
                    est_justifie=False
                )
                
    print("✅ Un mois complet de présences a été généré !")
    print("🚀 Tu peux maintenant retourner sur React et relancer la paie.")

simuler_mois_complet()