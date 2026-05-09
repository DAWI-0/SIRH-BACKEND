import os
import django

# ⚠️ Remplace 'nom_de_ton_projet' par le nom du dossier contenant ton settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from organization.models import Departement
from accounts.models import Employe
from django.db import transaction

# Base de données simulée : Sarah est RH, les autres chefs sont EMPLOYE
ENTREPRISE_DATA = {
    "Direction Générale": {
        "chef": {"username": "karim_pdg", "poste": "Directeur Général", "salaire": 45000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Leadership": 5, "Stratégie": 5, "Négociation": 5}},
        "employes": [
            {"username": "sanae", "poste": "Assistante de Direction", "salaire": 11000, "contrat": "CDI", "competences": {"Organisation": 5, "Communication": 5, "Anglais": 4}},
            {"username": "jalil", "poste": "Conseiller Stratégique", "salaire": 20000, "contrat": "CDI", "competences": {"Analyse de marché": 5, "Gestion de crise": 4}}
        ]
    },
    "Informatique & SI": {
        "chef": {"username": "ziad", "poste": "Directeur SI", "salaire": 25000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Management": 5, "Architecture SI": 5, "Cybersecurité": 4}},
        "employes": [
            {"username": "yassine", "poste": "Dev React", "salaire": 12000, "contrat": "CDI", "competences": {"React": 5, "JavaScript": 4, "Tailwind": 4}},
            {"username": "amine", "poste": "Dev Django", "salaire": 13000, "contrat": "CDI", "competences": {"Django": 5, "Python": 5, "PostgreSQL": 3}},
            {"username": "fatima", "poste": "Ingénieur DevOps", "salaire": 16000, "contrat": "CDI", "competences": {"Docker": 5, "CI/CD": 4, "Linux": 4}},
            {"username": "khalil", "poste": "Technicien Support", "salaire": 8000, "contrat": "CDD", "competences": {"Windows Server": 3, "Réseau": 3, "Support IT": 4}},
            {"username": "hassan", "poste": "Stagiaire Data", "salaire": 3000, "contrat": "STAGE", "competences": {"Python": 3, "SQL": 2, "PowerBI": 2}},
        ]
    },
    "Ressources Humaines": {
        "chef": {"username": "sarah", "poste": "Directrice RH", "salaire": 22000, "contrat": "CDI", "role": "RH", "competences": {"Stratégie RH": 5, "Droit Social": 4, "Management": 4}},
        "employes": [
            {"username": "meriem", "poste": "Chargée de Recrutement", "salaire": 9000, "contrat": "CDI", "competences": {"Sourcing": 4, "Entretiens": 5, "LinkedIn": 4}},
            {"username": "salma", "poste": "Gestionnaire Paie", "salaire": 10500, "contrat": "CDI", "competences": {"Sage": 5, "Comptabilité": 3, "Droit du travail": 4}},
            {"username": "othmane", "poste": "Assistant RH", "salaire": 6000, "contrat": "CDD", "competences": {"Administration": 3, "Pack Office": 4}},
            {"username": "leila", "poste": "Formatrice Interne", "salaire": 11000, "contrat": "CDI", "competences": {"Pédagogie": 5, "Communication": 5, "Conception": 3}},
            {"username": "mehdi", "poste": "Stagiaire RH", "salaire": 3000, "contrat": "STAGE", "competences": {"Organisation": 3, "Communication": 3}},
        ]
    },
    "Finance & Comptabilité": {
        "chef": {"username": "nadia", "poste": "Directrice Financière", "salaire": 24000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Finance": 5, "Audit": 4, "Management": 4}},
        "employes": [
            {"username": "youssef", "poste": "Comptable Senior", "salaire": 14000, "contrat": "CDI", "competences": {"Bilan": 5, "Fiscalité": 4, "Excel": 5}},
            {"username": "asmae", "poste": "Contrôleur de Gestion", "salaire": 15000, "contrat": "CDI", "competences": {"Analyse": 5, "Reporting": 4, "Excel": 5}},
            {"username": "ilyas", "poste": "Aide Comptable", "salaire": 6500, "contrat": "CDD", "competences": {"Saisie": 4, "Rigueur": 4}},
            {"username": "noura", "poste": "Auditeur Interne", "salaire": 12000, "contrat": "CDI", "competences": {"Audit": 4, "Conformité": 4, "Analyse": 3}},
            {"username": "tarik", "poste": "Stagiaire Finance", "salaire": 3000, "contrat": "STAGE", "competences": {"Excel": 3, "Comptabilité de base": 3}},
        ]
    },
    "Marketing & Communication": {
        "chef": {"username": "younes", "poste": "Directeur Marketing", "salaire": 21000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Stratégie Digitale": 5, "Branding": 5, "Management": 4}},
        "employes": [
            {"username": "imane", "poste": "Community Manager", "salaire": 8500, "contrat": "CDI", "competences": {"Réseaux Sociaux": 5, "Copywriting": 4, "Canva": 4}},
            {"username": "bilal", "poste": "Spécialiste SEO", "salaire": 11000, "contrat": "CDI", "competences": {"SEO": 5, "Google Analytics": 4, "HTML/CSS": 3}},
            {"username": "rania", "poste": "Graphiste", "salaire": 9500, "contrat": "CDI", "competences": {"Illustrator": 5, "Photoshop": 5, "Figma": 3}}
        ]
    },
    "Ventes & Commercial": {
        "chef": {"username": "mourad", "poste": "Directeur Commercial", "salaire": 26000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Vente B2B": 5, "Négociation": 5, "CRM": 4}},
        "employes": [
            {"username": "soufiane", "poste": "Key Account Manager", "salaire": 16000, "contrat": "CDI", "competences": {"Relation Client": 5, "Fidélisation": 4, "Salesforce": 4}},
            {"username": "hind", "poste": "Commerciale Terrain", "salaire": 10000, "contrat": "CDI", "competences": {"Prospection": 5, "Permis B": 5, "Ténacité": 4}},
            {"username": "youssef_v", "poste": "Sales Ops", "salaire": 12000, "contrat": "CDD", "competences": {"Analyse de données": 4, "Automatisation": 3, "CRM": 5}}
        ]
    },
    "Logistique & Achats": {
        "chef": {"username": "jalal", "poste": "Directeur Supply Chain", "salaire": 23000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Supply Chain": 5, "Négociation": 4, "ERP": 5}},
        "employes": [
            {"username": "fadwa", "poste": "Acheteuse IT", "salaire": 13000, "contrat": "CDI", "competences": {"Sourcing Fournisseurs": 4, "Contrats": 4, "Matériel IT": 4}},
            {"username": "omar", "poste": "Gestionnaire de Stock", "salaire": 8000, "contrat": "CDI", "competences": {"Logistique": 4, "Inventaire": 5, "SAP": 3}}
        ]
    },
    "Recherche & Développement": {
        "chef": {"username": "tariq", "poste": "Directeur R&D", "salaire": 27000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Innovation": 5, "Gestion de Projet": 5, "IA": 4}},
        "employes": [
            {"username": "meryem", "poste": "Ingénieur Innovation", "salaire": 17000, "contrat": "CDI", "competences": {"Prototypage": 5, "IoT": 4, "Recherche": 5}},
            {"username": "brahim", "poste": "Data Scientist", "salaire": 18000, "contrat": "CDI", "competences": {"Machine Learning": 5, "Python": 5, "Statistiques": 4}}
        ]
    },
    "Juridique & Conformité": {
        "chef": {"username": "kenza", "poste": "Directrice Juridique", "salaire": 24000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Droit des Affaires": 5, "Conformité": 5, "Rédaction de contrats": 5}},
        "employes": [
            {"username": "ali", "poste": "Juriste d'Entreprise", "salaire": 13000, "contrat": "CDI", "competences": {"Droit commercial": 4, "RGPD": 4, "Veille juridique": 4}},
            {"username": "houda", "poste": "Chargée de Conformité", "salaire": 11500, "contrat": "CDD", "competences": {"Audit légal": 4, "Normes ISO": 3, "Ethique": 4}}
        ]
    },
    "Services Généraux": {
        "chef": {"username": "rachid", "poste": "Responsable Services Généraux", "salaire": 15000, "contrat": "CDI", "role": "EMPLOYE", "competences": {"Facility Management": 5, "Sécurité": 4, "Gestion prestataires": 4}},
        "employes": [
            {"username": "kawtar", "poste": "Hôtesse d'Accueil", "salaire": 5000, "contrat": "CDI", "competences": {"Accueil": 5, "Standard téléphonique": 5, "Anglais": 3}},
            {"username": "driss", "poste": "Technicien Bâtiment", "salaire": 6000, "contrat": "CDI", "competences": {"Électricité": 4, "Plomberie": 4, "Maintenance": 5}}
        ]
    }
}

@transaction.atomic
def run_seed():
    print("🧹 Nettoyage de la base de données...")
    Employe.objects.all().delete()
    Departement.objects.all().delete()

    print("⏳ Génération de l'entreprise Smart Enterprise en cours...")
    matricule_counter = 1
    domaine_email = "@smart-enterprise.com"

    for nom_dept, donnees in ENTREPRISE_DATA.items():
        # 1. Créer le département
        dept = Departement.objects.create(nom_departement=nom_dept)
        
        # 2. Créer le Chef
        chef_data = donnees["chef"]
        chef = Employe.objects.create(
            username=chef_data["username"],
            email=f"{chef_data['username']}{domaine_email}",
            matricule=f"EMP-{matricule_counter:03d}",
            poste_titre=chef_data["poste"],
            departement=dept,
            role=chef_data["role"], # Sarah sera RH, les autres EMPLOYE
            salaire=chef_data["salaire"],
            type_contrat=chef_data["contrat"],
            statut="ACTIF",
            matrice_competences=chef_data["competences"]
        )
        chef.set_password("Test1234!")
        chef.save()
        matricule_counter += 1

        # Assigner le chef au département ! C'est ce qui te permettra de gérer tes autorisations
        dept.manager = chef
        dept.save()

        # 3. Créer les employés du département
        for emp_data in donnees["employes"]:
            emp = Employe.objects.create(
                username=emp_data["username"],
                email=f"{emp_data['username']}{domaine_email}",
                matricule=f"EMP-{matricule_counter:03d}",
                poste_titre=emp_data["poste"],
                departement=dept,
                role="EMPLOYE",
                salaire=emp_data["salaire"],
                type_contrat=emp_data["contrat"],
                statut="ACTIF",
                matrice_competences=emp_data["competences"]
            )
            emp.set_password("Test1234!")
            emp.save()
            matricule_counter += 1
            
    print(f"\n🚀 SUCCÈS ! Profils créés. Sarah est RH, les autres sont Employés.")

# Lancement automatique pour ta commande shell
run_seed()