from django.urls import re_path
from dmapjt.monitoring.consumers import VideoWebsocketConsumer

websocket_urlpatterns = [
    re_path('ws/video/', VideoWebsocketConsumer.as_asgi()),  # WebSocket 경로 설정
]