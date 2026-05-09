from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PointageIoT

class PointageIoTListView(APIView):
    def get(self, request):
        # On récupère les pointages du plus récent au plus ancien
        pointages = PointageIoT.objects.all().order_by('-timestamp')
        
        data = []
        for p in pointages:
            data.append({
                "timestamp": p.timestamp,
                "employe_name": p.employe.username, # 👈 IMPORTANT: React cherche ce nom
                "matricule": p.employe.matricule,
                "type_pointage": p.type_pointage,
                "id_capteur": p.id_capteur,
                "est_justifie": p.est_justifie
            })
        return Response(data)

    def delete(self, request):
        PointageIoT.objects.all().delete()
        return Response({"message": "Historique vidé"})