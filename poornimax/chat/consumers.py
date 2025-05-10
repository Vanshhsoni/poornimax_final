import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_name = self.username
        self.room_group_name = f"chat_{self.room_name}"
        
        # Get the user objects
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            # Reject the connection if user is not authenticated
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        sender = text_data_json.get('sender', '')

        if message and not self.user.is_anonymous:
            # Save message to database
            other_user = await self.get_user_by_username(self.username)
            if other_user:
                await self.save_message(self.user, other_user, message)
                
                # Send message to the current user's room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': self.user.username,
                    }
                )
                
                # Also send message to the recipient's room
                recipient_room = f"chat_{self.user.username}"
                await self.channel_layer.group_send(
                    recipient_room,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': self.user.username,
                    }
                )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
    
    @database_sync_to_async
    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_message(self, sender, receiver, content):
        Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )