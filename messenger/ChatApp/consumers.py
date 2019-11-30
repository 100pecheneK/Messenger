from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

# from ChatApp.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # print(self.scope['url_route']['kwargs']['room_name'])
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print('Соединение установлено!')

        await self.send(json.dumps({
            'still_online': 'True',
            # 'still_online': still_online,
        }))

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

            #Занесение сообщения в БД
            # create_message(content = message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

    # Receive message from room group

    async def chat_message(self, event):
        if (event['message']):
            message = event['message']

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
            }))

    # @database_sync_to_async
    # def create_message(self, content):
    #     Message.objects.create(content=content)
