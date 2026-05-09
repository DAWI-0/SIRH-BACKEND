import os
import django
from django.utils import timezone

# ⚠️ N'oublie pas le nom de ton projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nom_de_ton_projet.settings')
django.setup()

from attendance.models import PointageIoT
from accounts.models import Employe

def test_propre():
    print("🧹 Nettoyage de tous les pointages...")
    PointageIoT.objects.all().delete()

    employes = Employe.objects.filter(statut='ACTIF')
    if employes.count() < 2:
        print("Erreur : Il te faut au moins 2 employés dans la base.")
        return

    emp_conforme = employes[0]
    emp_retard = employes[1]
    
    maintenant = timezone.localtime() # Heure locale (Casablanca)

    print("✅ Création d'un pointage CONFORME (08h45)...")
    p1 = PointageIoT.objects.create(employe=emp_conforme, type_pointage='ENTREE', id_capteur='TEST_MANUEL')
    # On force l'heure à 08h45
    PointageIoT.objects.filter(id=p1.id).update(timestamp=maintenant.replace(hour=8, minute=45))

    print("❌ Création d'un pointage RETARD (09h20)...")
    p2 = PointageIoT.objects.create(employe=emp_retard, type_pointage='ENTREE', id_capteur='TEST_MANUEL')
    # On force l'heure à 09h20
    PointageIoT.objects.filter(id=p2.id).update(timestamp=maintenant.replace(hour=9, minute=20))

    print("🚀 Test terminé ! Va vérifier sur React.")

test_propre()