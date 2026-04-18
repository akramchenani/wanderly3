import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Conversation, Message
from accounts.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message', '')
        user = self.scope['user']
        if not user.is_authenticated or not message_content.strip():
            return
        message = await self.save_message(user, message_content)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': user.username,
                'sender_id': user.pk,
                'timestamp': str(message.created_at.strftime('%H:%M')),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_message(self, user, content):
        conversation = Conversation.objects.get(pk=self.conversation_id)
        return Message.objects.create(conversation=conversation, sender=user, content=content)
