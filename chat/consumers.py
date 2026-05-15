import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            print("❌ WebSocket Rejeté : Utilisateur non authentifié")
            await self.close()
            return
            
        self.room_group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ WebSocket Connecté : {self.user.username} (Room: {self.room_group_name})")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            print(f"🔌 WebSocket Déconnecté : {self.user.username}")

    async def receive(self, text_data):
        """Gère les messages entrants (ping, etc.)"""
        try:
            data = json.loads(text_data)
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({"type": "pong"}))
        except Exception as e:
            print(f"⚠️ Erreur receive: {e}")

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))