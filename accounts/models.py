import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Le modèle parent (Sécurité et Rôles)
class Utilisateur(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('RH', 'Manager RH'),
        ('EMPLOYE', 'Employé'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYE')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# 2. Le modèle Employé
class Employe(Utilisateur):
    STATUT_CHOICES=[
        ('ACTIF','Actif'),
        ('DEMISSIONNAIRE','Demissionnaire'),
        ('CONGE','Congé'),
        ('LICENCIE','Licencié'),
    ]
    TYPE_CONTRAT_CHOICES = [
        ('CDI', 'CDI'),
        ('CDD', 'CDD'),
        ('STAGE', 'Stage'),
        ('FREELANCE', 'Freelance'),
    ]
    matricule = models.CharField(max_length=50, unique=True)
    solde_conges = models.FloatField(default=22.5)
    poste_titre = models.CharField(max_length=100)
    matrice_competences = models.JSONField(default=list, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES, default='CDI')
    salaire = models.FloatField(default=0)
    
    # La magie du multi-applications : on pointe vers l'app "organization" !
    departement = models.ForeignKey(
        'organization.Departement', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employes'
    )

    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"


# 3. Les Proxy Models (Pour respecter l'UML)
class ManagerRH(Utilisateur):
    class Meta:
        proxy = True
        verbose_name = "Manager RH"
        verbose_name_plural = "Managers RH"

class Administrateur(Utilisateur):
    class Meta:
        proxy = True
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"


# 👇 À ajouter à la fin de ton fichier models.py

class ArchiveEmploye(models.Model):
    MOTIF_DEPART_CHOICES = [
        ('DEMISSIONNAIRE', 'Démission'),
        ('LICENCIE', 'Licenciement'),
        ('FIN_CDD', 'Fin de contrat CDD'),
        ('RETRAITE', 'Départ en retraite'),
    ]
    
    username = models.CharField(max_length=150)
    matricule = models.CharField(max_length=50)
    poste_titre = models.CharField(max_length=100, null=True, blank=True)
    departement_nom = models.CharField(max_length=100, null=True, blank=True)
    date_depart = models.DateField(null=True, blank=True)
    
    # C'est ce champ qui nous dira POURQUOI il est dans les archives
    statut_depart = models.CharField(max_length=50, choices=MOTIF_DEPART_CHOICES)
    
    matrice_competences_archive = models.JSONField(default=list, blank=True, null=True)

    class Meta:
        verbose_name = "Archive Employé"
        verbose_name_plural = "Archives Employés"

    def __str__(self):
        return f"{self.username} - {self.get_statut_depart_display()}"