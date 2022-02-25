import imp
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from social_media.models import AppUser
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_{}'.format(self.room_name)
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def receive(self, text_data):
        text_data_dict = json.loads(text_data)
        message = text_data_dict['message']
        username = text_data_dict['username']
        profile_image_path = text_data_dict['profile_image_path']
        
        # save message into database
        await self.save_message_to_db(message)
        
        # send to all user in the connection
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'profile_image_path': profile_image_path
            }
        )
        
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        profile_image_path = event['profile_image_path']
        
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'profile_image_path': profile_image_path
        }))
        
    @sync_to_async
    def save_message_to_db(self, message):
        sender = AppUser.objects.get(email=self.scope['user'])
        receiver = None

        # retrieve receiver from room_name
        room_name = self.scope['url_route']['kwargs']['room_name'];
        user_ids = room_name.split('_')
        if int(user_ids[0]) == sender.pk:
            receiver = AppUser.objects.get(pk=int(user_ids[1]))
        else:
            receiver = AppUser.objects.get(pk=int(user_ids[0]))
        
        new_message = Message.objects.create(sender=sender, receiver=receiver, content=message)
        new_message.save()