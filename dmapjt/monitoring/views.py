# views.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'video_{self.room_name}'

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

    async def receive(self, text_data):
        data = json.loads(text_data)
        # 여기에서 클라이언트로부터 받은 메시지를 처리할 수 있습니다.

        # 예: 클라이언트로 응답 보내기
        await self.send(text_data=json.dumps({
            'result': 'Drowsy driving detected'  # 예시로 응답
        }))

    async def send_message_to_group(self, event):
        # 메시지 전달 (웹소켓 메시지)
        await self.send(text_data=json.dumps({
            'result': event['result'],
        }))
