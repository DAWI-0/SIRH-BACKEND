import uuid
from django.db import models

class PointageIoT(models.Model):
    # Les choix possibles pour le type de pointage
    TYPE_CHOICES = (
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employe = models.ForeignKey('accounts.Employe', on_delete=models.CASCADE, related_name='pointages')
    type_pointage = models.CharField(max_length=10, choices=TYPE_CHOICES, default='ENTREE') # <-- LE NOUVEAU CHAMP
    timestamp = models.DateTimeField(auto_now_add=True)
    id_capteur = models.CharField(max_length=50)
    est_justifie = models.BooleanField(default=False)

    def __str__(self):
        # Affiche proprement : "Entrée - EMP-001 (2026-04-29 14:28)"
        return f"{self.get_type_pointage_display()} - {self.employe} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"

