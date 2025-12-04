import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage

logger = logging.getLogger(__name__)
User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    #presencia simple en memoria: conexiones por sala (no distribuido)
    room_connections = {}
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        logger.info(f"WebSocket connecting to room: {self.room_name}")

        #join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        #track presence
        room_set = self.room_connections.setdefault(self.room_group_name, set())
        room_set.add(self.channel_name)
        
        users_count = len(room_set)
        logger.info(f"User connected to {self.room_name}. Total connections: {users_count}")

        #broadcast updated users_online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence',
                'users_online': users_count
            }
        )

    async def disconnect(self, close_code):
        #leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        #update presence
        room_set = self.room_connections.get(self.room_group_name)
        if room_set and self.channel_name in room_set:
            room_set.discard(self.channel_name)
            users_count = len(room_set)
            logger.info(f"User disconnected from {self.room_name}. Remaining connections: {users_count}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'presence',
                    'users_online': users_count
                }
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']

        if user.is_authenticated:
            #save message to database
            chat_message = await self.save_message(user, message)
            
            #send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_name': user.username,
                    'username': user.username,
                    'timestamp': chat_message.fecha_envio.isoformat()
                }
            )

    async def chat_message(self, event):
        #send message to websocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user_name': event['user_name'],
            'username': event['username'],
            'timestamp': event['timestamp']
        }))

    async def presence(self, event):
        #send presence updates
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'users_online': event.get('users_online', 0)
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        return ChatMessage.objects.create(
            usuario=user,
            usuario_nombre=user.username,
            contenido=message,
            sala=self.room_name,
            tipo='user'
        )
