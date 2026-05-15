from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.exceptions import PermissionDenied
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
import traceback 

class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', '') in ['RH', 'ADMIN', 'ADMINISTRATEUR']:
            return Conversation.objects.filter(hr=user).prefetch_related('messages')
        return Conversation.objects.filter(employee=user).prefetch_related('messages')


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        conv_id = self.kwargs['conv_id']
        user = self.request.user
        try:
            conv = Conversation.objects.get(id=conv_id)
            if conv.employee != user and conv.hr != user:
                raise PermissionDenied("Non autorisé.")
        except Conversation.DoesNotExist:
            return Message.objects.none()
        return Message.objects.filter(conversation_id=conv_id)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        print(f"\n{'='*60}")
        print(f"🔔 SENDMESSAGE: user={request.user} | id={request.user.id} | role={getattr(request.user, 'role', 'NO ROLE')}")
        
        try:
            user = request.user
            content = request.data.get('content', '').strip()
            receiver_ids = request.data.get('receiver_ids', [])
            
            print(f"📨 Data: content='{content[:30]}...' | receivers={receiver_ids} | type={type(receiver_ids).__name__}")

            if not content:
                return Response({"error": "Contenu requis"}, status=400)
            if not receiver_ids:
                return Response({"error": "Destinataires requis"}, status=400)

            is_hr = getattr(user, 'role', '') in ['RH', 'ADMIN', 'ADMINISTRATEUR']
            channel_layer = get_channel_layer()
            
            if channel_layer is None:
                print("❌ CHANNEL_LAYER = None")
                return Response({"error": "Channel Layer non configuré"}, status=500)
            print(f"✅ ChannelLayer: {type(channel_layer).__name__}")

            sent_messages = []

            # Message global
            if receiver_ids == 'all' or (isinstance(receiver_ids, list) and receiver_ids == ['all']):
                if not is_hr:
                    return Response({"error": "Seul le RH peut envoyer un message global"}, status=403)
                
                from django.contrib.auth import get_user_model
                User = get_user_model()
                employees = User.objects.filter(role__in=['EMPLOYE', 'EMPLOYEE', 'EMPLOYÉ'])
                
                for emp in employees:
                    if emp.id == user.id:
                        continue
                    conv, _ = Conversation.objects.get_or_create(employee=emp, hr=user)
                    msg = Message.objects.create(conversation=conv, sender=user, content=content)
                    msg_data = self._serialize_message(msg)
                    sent_messages.append(msg_data)
                    
                    room = f"user_{str(emp.id)}"
                    print(f"📡 [GLOBAL] Envoi à room: {room}")
                    async_to_sync(channel_layer.group_send)(
                        room,
                        {"type": "chat_message", "message": msg_data}
                    )
                
                room_me = f"user_{str(user.id)}"
                print(f"📡 [GLOBAL] Notif RH à room: {room_me}")
                async_to_sync(channel_layer.group_send)(
                    room_me,
                    {"type": "chat_message", "message": {"action": "refresh_conversations"}}
                )
                print(f"{'='*60}\n")
                return Response(sent_messages, status=status.HTTP_201_CREATED)

            # Message individuel
            if not isinstance(receiver_ids, list):
                receiver_ids = [receiver_ids]  # ← Gérer le cas string unique

            for rec_id in receiver_ids:
                if not rec_id:
                    continue
                
                rec_id_str = str(rec_id)
                print(f"➡️ Traitement rec_id={rec_id_str} (type={type(rec_id).__name__})")

                if is_hr:
                    conv, created = Conversation.objects.get_or_create(employee_id=rec_id, hr=user)
                    target_ws_id = rec_id_str
                    print(f"   [RH→Employé] Conv: id={conv.id} | created={created}")
                else:
                    conv, created = Conversation.objects.get_or_create(employee=user, hr_id=rec_id)
                    target_ws_id = rec_id_str
                    print(f"   [Employé→RH] Conv: id={conv.id} | created={created}")

                msg = Message.objects.create(conversation=conv, sender=user, content=content)
                msg_data = self._serialize_message(msg)
                sent_messages.append(msg_data)
                print(f"   Message créé: id={msg.id}")

                # Notifier destinataire
                room_target = f"user_{target_ws_id}"
                print(f"   📡 Envoi destinataire → room: {room_target}")
                try:
                    async_to_sync(channel_layer.group_send)(
                        room_target,
                        {"type": "chat_message", "message": msg_data}
                    )
                    print(f"   ✅ WS destinataire OK")
                except Exception as e:
                    print(f"   ❌ WS destinataire ERREUR: {e}")

                # Notifier expéditeur
                room_me = f"user_{str(user.id)}"
                print(f"   📡 Envoi expéditeur → room: {room_me}")
                try:
                    async_to_sync(channel_layer.group_send)(
                        room_me,
                        {"type": "chat_message", "message": msg_data}
                    )
                    print(f"   ✅ WS expéditeur OK")
                except Exception as e:
                    print(f"   ❌ WS expéditeur ERREUR: {e}")

            print(f"{'='*60}\n")
            return Response(sent_messages, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("🔥 ERREUR 500:")
            print(traceback.format_exc())
            print(f"{'='*60}\n")
            return Response({"error": "Erreur serveur", "detail": str(e)}, status=500)

    def _serialize_message(self, msg):
        data = MessageSerializer(msg).data
        data['id'] = str(data['id'])
        data['conversation_id'] = str(data['conversation_id'])
        data['sender_id'] = str(data['sender_id'])
        data['created_at'] = str(data['created_at'])
        return data