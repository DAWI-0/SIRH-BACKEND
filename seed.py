from organization.models import Departement
from accounts.models import Employe
from django.db import transaction

# Nos données avec les compétences ajoutées
ENTREPRISE_DATA = {
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
    }
}

@transaction.atomic
def run_seed():
    print("⏳ Mise à jour et génération des données SIRH avec Emails et Compétences...")
    matricule_counter = 1
    domaine_email = "@smart-enterprise.com"

    for nom_dept, donnees in ENTREPRISE_DATA.items():
        # 1. Créer ou récupérer le département
        dept, created = Departement.objects.get_or_create(nom_departement=nom_dept)
        
        # 2. Créer ou Mettre à jour le Chef
        chef_data = donnees["chef"]
        chef, created = Employe.objects.update_or_create(
            username=chef_data["username"],
            defaults={
                "email": f"{chef_data['username']}{domaine_email}", # Génération de l'email
                "matricule": f"EMP-{matricule_counter:03d}",
                "poste_titre": chef_data["poste"],
                "departement": dept,
                "role": chef_data["role"],
                "salaire": chef_data["salaire"],
                "type_contrat": chef_data["contrat"],
                "statut": "ACTIF",
                "matrice_competences": chef_data["competences"] # Ajout de la matrice
            }
        )
        # On ne change le mot de passe que si c'est une nouvelle création
        if created:
            chef.set_password("Test1234!")
            chef.save()
        matricule_counter += 1

        # Assigner le chef au département
        dept.manager = chef
        dept.save()

        # 3. Créer ou Mettre à jour les employés du département
        for emp_data in donnees["employes"]:
            emp, created = Employe.objects.update_or_create(
                username=emp_data["username"],
                defaults={
                    "email": f"{emp_data['username']}{domaine_email}", # Génération de l'email
                    "matricule": f"EMP-{matricule_counter:03d}",
                    "poste_titre": emp_data["poste"],
                    "departement": dept,
                    "role": "EMPLOYE",
                    "salaire": emp_data["salaire"],
                    "type_contrat": emp_data["contrat"],
                    "statut": "ACTIF",
                    "matrice_competences": emp_data["competences"] # Ajout de la matrice
                }
            )
            if created:
                emp.set_password("Test1234!")
                emp.save()
            matricule_counter += 1
            
    print(f"\n🚀 SUCCÈS ! Les profils ont été mis à jour avec les Emails (@smart-enterprise.com) et les Matrices de Compétences.")

run_seed()