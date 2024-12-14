from channels.generic.websocket import AsyncWebsocketConsumer
from PIL import Image
import io
import json
import torch
import numpy as np
import pathlib
from pathlib import Path

class VideoWebsocketConsumer(AsyncWebsocketConsumer):
    # PosixPath를 WindowsPath로 대체하는 방법
    pathlib.PosixPath = pathlib.WindowsPath

    async def connect(self):
        # 웹소켓 연결을 수락합니다.
        await self.accept()

        # YOLO 모델 초기화
        model_path_seat_belt = pathlib.Path("C:/DjangoProject/dma-django/dmapjt/monitoring/models/best.pt")
        self.seat_belt_model = torch.hub.load(
            "ultralytics/yolov5", 
            "custom", 
            path=model_path_seat_belt,
            force_reload=True
        )
        
        model_path_drowsy = pathlib.Path("C:/DjangoProject/dma-django/dmapjt/monitoring/models/drbest.pt")
        self.drowsy_model = torch.hub.load(
            "ultralytics/yolov5", 
            "custom", 
            path=model_path_drowsy,
            force_reload=True
        )

        # 방 그룹에 참여합니다.
        await self.channel_layer.group_add(
            "video",
            self.channel_name
        )

    async def disconnect(self, close_code):
        # 방 그룹에서 이 채널을 제거합니다.
        await self.channel_layer.group_discard(
            "video",
            self.channel_name
        )

    async def receive(self, bytes_data=None):
        """
        WebSocket으로부터 이미지 데이터를 수신하여 처리
        """
        if bytes_data:  # 이미지 바이너리 데이터 수신
            try:
                # 이미지를 PIL 형식으로 변환
                image = Image.open(io.BytesIO(bytes_data))

                # 딥러닝 모델 분석 호출
                result = self.process_image(image)

                # 분석 결과를 클라이언트로 전송
                await self.send(json.dumps(result))

            except Exception as e:
                # 오류 발생 시
                await self.send(json.dumps({
                    "error": f"Error processing image: {str(e)}"
                }))

    def process_image(self, image):
        """
        이미지에서 안전벨트와 졸음운전을 감지하고 결과를 반환
        """
        # PIL 이미지를 numpy 배열로
        image_array = np.array(image)

        # 모델 예측
        seat_belt_results = self.seat_belt_model(image_array)
        drowsy_results = self.drowsy_model(image_array)

        # 감지 결과 분석
        seat_belt_detected = any(label in seat_belt_results.names for label in ["seat_belt"])
        drowsy_detected = any(label in drowsy_results.names for label in ["Leye", "Reye"])

        # 결과 메시지 생성
        results = {}
        if not seat_belt_detected:
            results['seat_belt'] = "안전벨트를 착용하지 않았습니다."
        else:
            results['seat_belt'] = "안전벨트를 착용했습니다."

        if not drowsy_detected:
            results['drowsy'] = "졸음운전이 감지되었습니다. 주의하세요!"
        else:
            results['drowsy'] = "졸음운전이 감지되지 않았습니다."

        return results
