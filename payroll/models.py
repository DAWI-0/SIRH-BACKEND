import uuid
from django.db import models

class Contrat(models.Model):
    TYPE_CHOICES = [('CDI', 'CDI'), ('CDD', 'CDD'), ('STAGE', 'Stage')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey('accounts.Employe', on_delete=models.CASCADE, related_name='contrats')
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    type_contrat = models.CharField(max_length=20, choices=TYPE_CHOICES)
    salaire_mensuel = models.DecimalField(max_digits=10, decimal_places=2)
    jours_preavis = models.IntegerField(default=30)

    def __str__(self):
        return f"Contrat {self.type_contrat}"

class Evaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey('accounts.Employe', on_delete=models.CASCADE, related_name='evaluations')
    date_evaluation = models.DateField()
    note_comportementale = models.FloatField()
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evaluation - {self.employe} - {self.date_evaluation}"

class FichePaie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey('accounts.Employe', on_delete=models.CASCADE, related_name='fiches_paie')
    periode_mois = models.IntegerField()
    periode_annee = models.IntegerField()
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2)
    deductions_absences = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # 👇 On remplace primes_evaluation par primes_supp
    primes_supp = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    net_a_payer = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Paie {self.employe} - {self.periode_mois}/{self.periode_annee}"
# 👇 La classe Conge est maintenant bien séparée et alignée à gauche ! 👇
class Conge(models.Model):
    TYPE_CONGE = [
        ('ANNUEL', 'Congé Annuel'),
        ('MALADIE', 'Congé Maladie'),
        ('EXCEPTIONNEL', 'Congé Exceptionnel'),
    ]
    
    STATUT_CONGE = [
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVE', 'Approuvé'),
        ('REFUSE', 'Refusé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey('accounts.Employe', on_delete=models.CASCADE, related_name='conges_list')
    type_conge = models.CharField(max_length=20, choices=TYPE_CONGE, default='ANNUEL')
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CONGE, default='EN_ATTENTE')
    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employe} - {self.type_conge} ({self.statut})"
class PresenceManuelle(models.Model):
    STATUT_CHOICES = [
        ('PRESENT', 'Présent'), # Bulle Verte
        ('ABSENT', 'Absent'),   # Bulle Rouge
        ('SUPP', 'Jour Supp/Weekend'), # Bulle Jaune
        ('REPOS', 'Jour de Repos'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey('accounts.Employe', on_delete=models.CASCADE, related_name='presences_manuelles')
    date_jour = models.DateField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='PRESENT')

    class Meta:
        # Empêche d'avoir deux statuts pour le même jour et le même employé
        unique_together = ('employe', 'date_jour') 

    def __str__(self):
        return f"{self.employe} - {self.date_jour} : {self.statut}"        