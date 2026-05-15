import os
import sys
import random
import calendar
from datetime import date, datetime, time

# 1. Configuration stricte de l'environnement Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.utils import timezone
from accounts.models import Employe
from payroll.models import FichePaie, PresenceManuelle
from attendance.models import PointageIoT 

def simuler_mois_mai():
    ANNEE = 2026 
    MOIS = 5     

    print(f"🧹 Nettoyage des anciens pointages et fiches de paie...")
    PointageIoT.objects.all().delete()
    PresenceManuelle.objects.all().delete()
    FichePaie.objects.all().delete()

    employes = Employe.objects.filter(statut='ACTIF')
    employes_supp = employes.filter(username__in=['khalil', 'imane', 'youssef_v'])
    jours_dans_le_mois = calendar.monthrange(ANNEE, MOIS)[1]

    print(f"⏳ Génération intelligente avec jours de REPOS pour Mai ({jours_dans_le_mois} jours)...")
    
    for jour in range(1, jours_dans_le_mois + 1):
        date_jour = date(ANNEE, MOIS, jour)
        jour_semaine = date_jour.weekday() 
        est_weekend = jour_semaine >= 5

        for employe in employes:
            if est_weekend:
                # 10% de chance de prime SUPP pour les employés spéciaux
                if employe in employes_supp and random.random() < 0.10:
                    PresenceManuelle.objects.create(
                        employe=employe,
                        date_jour=date_jour,
                        statut='SUPP'
                    )
                else:
                    # 👇 CORRECTION ICI : On insère explicitement 'REPOS' pour griser la bulle !
                    PresenceManuelle.objects.create(
                        employe=employe,
                        date_jour=date_jour,
                        statut='REPOS'
                    )
            else:
                est_present = random.random() > 0.03 
                
                if est_present:
                    heure_arrivee = time(hour=8, minute=random.randint(30, 59))
                    dt_pointage = timezone.make_aware(datetime.combine(date_jour, heure_arrivee))

                    PointageIoT.objects.create(
                        employe=employe,
                        type_pointage='ENTREE',
                        timestamp=dt_pointage, 
                        id_capteur='SIMULATION_MAI',
                        est_justifie=False
                    )
                    
                    PresenceManuelle.objects.create(
                        employe=employe,
                        date_jour=date_jour,
                        statut='PRESENT'
                    )
                else:
                    PresenceManuelle.objects.create(
                        employe=employe,
                        date_jour=date_jour,
                        statut='ABSENT'
                    )
                
    print(f"✅ Mois de Mai {ANNEE} généré avec succès avec tous les week-ends en REPOS !")

if __name__ == '__main__':
    simuler_mois_mai()