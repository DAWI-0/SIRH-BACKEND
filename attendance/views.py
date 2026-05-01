from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PointageIoTSerializer # Assure-toi que c'est le bon nom de ton serializer

class IoTPontageView(APIView):
    # Pour l'instant on désactive l'authentification par token utilisateur 
    # car c'est une machine (l'ESP32) qui envoie la donnée
    permission_classes = [] 
    authentication_classes = []

    def post(self, request):
        # 1. On donne les données JSON reçues (request.data) au Serializer
        serializer = PointageIoTSerializer(data=request.data)
        
        # 2. Le Serializer vérifie si les données sont propres et correspondent à ton Modèle
        if serializer.is_valid():
            # 3. LA LIGNE MAGIQUE : Sauvegarde réelle dans la base PostgreSQL
            serializer.save() 
            
            # On dit au Bridge que tout s'est bien passé
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Si la donnée est mauvaise (ex: format de date incorrect), on renvoie une erreur
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)