import os
import sys

# 1. Configuration stricte de l'environnement Django AVANT les imports Django
# Assurez-vous que le chemin racine du projet est dans sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 2. Initialisation de Django (C'est cette partie qui posait problème)
import django
django.setup()

# 3. SEULEMENT APRÈS django.setup(), on importe les modèles
from django.utils import timezone
import random
from datetime import timedelta
from accounts.models import Employe
from payroll.models import FichePaie, PresenceManuelle
from attendance.models import PointageIoT 

def simuler_mois_complet():
    print("🧹 Nettoyage des anciens pointages et fiches de paie...")
    PointageIoT.objects.all().delete()
    PresenceManuelle.objects.all().delete()
    FichePaie.objects.all().delete()

    employes = Employe.objects.filter(statut='ACTIF')
    maintenant = timezone.localtime()
    
    print(f"⏳ Génération de 26 jours de pointages pour {employes.count()} employés...")
    
    for i in range(26):
        date_jour = maintenant - timedelta(days=(26 - i))
        
        for employe in employes:
            # 95% de chance d'être présent
            est_present = random.random() > 0.05 
            
            if est_present:
                PointageIoT.objects.create(
                    employe=employe,
                    type_pointage='ENTREE',
                    timestamp=date_jour.replace(hour=8, minute=45), 
                    id_capteur='SIMULATION_MOIS',
                    est_justifie=False
                )
                
                PresenceManuelle.objects.create(
                    employe=employe,
                    date_jour=date_jour.date(),
                    statut='PRESENT'
                )
            else:
                PresenceManuelle.objects.create(
                    employe=employe,
                    date_jour=date_jour.date(),
                    statut='ABSENT'
                )
                
    print("✅ Un mois complet de présences a été généré !")
    print("🚀 Tu peux maintenant retourner sur React et relancer la paie.")

# Lancement de la fonction
if __name__ == '__main__':
    simuler_mois_complet()