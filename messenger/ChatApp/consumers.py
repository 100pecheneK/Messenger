from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.contrib.auth.models import User
from .models import *


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print('Соединение установлено!')


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if 'message' in text_data_json:
            message = text_data_json['message']
            author_login = text_data_json['author']
            current_room_name = text_data_json['current_room_name']
            #Занесение сообщения в БД
            await self.create_message(content=message, author_login=author_login, current_room_name=current_room_name)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'author': author_login,
                }
            )

    # Receive message from room group

    async def chat_message(self, event):
        if event['message']:
            message = event['message']
            author_login = event['author']

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'author': author_login,
            }))

    @database_sync_to_async
    def create_message(self, content, author_login, current_room_name):
        try:
            user = User.objects.get(username=author_login)
            current_room = Room.objects.get(name=current_room_name)
            Message.objects.create(content=content, author=user, room=current_room)
        except User.DoesNotExist:
            print('User doesnt exists.')


    # @database_sync_to_async
    # def create_or_fetch_room(self, room_name, first_user, second_user):
    #     try:
    #         room = Room.objects.get(name=room_name)
    #     except:
    #         first_u = User.objects.get(username=first_user)
    #         second_u = User.objects.get(username=second_user)
    #         Room.objects.create()

