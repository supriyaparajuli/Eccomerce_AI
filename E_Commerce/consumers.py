from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from app.models import ChatRoom, Message
import datetime

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        message = content.get('message')

        if message:
            # Save the message to the database
            sender = self.scope['user']
            chat_room = await self.get_chat_room()
            receiver = await self.get_receiver(sender, chat_room)
            new_message = await self.create_message(sender, receiver, message, chat_room)

            # Get the current timestamp
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Send the message to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username,
                    'timestamp': timestamp
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        # Send the message to the WebSocket
        await self.send_json({
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        })

    @database_sync_to_async
    def get_chat_room(self):
        return ChatRoom.objects.get(id=self.room_id)

    @database_sync_to_async
    def get_receiver(self, sender, chat_room):
        if sender == chat_room.participant1:
            return chat_room.participant2
        else:
            return chat_room.participant1

    @database_sync_to_async
    def create_message(self, sender, receiver, content, chat_room):
        return Message.objects.create(sender=sender, receiver=receiver, content=content, chat_room=chat_room)
