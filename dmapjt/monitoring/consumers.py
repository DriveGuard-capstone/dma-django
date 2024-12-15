from channels.generic.websocket import AsyncWebsocketConsumer
from PIL import Image
import io
import json
import torch
import numpy as np
import pathlib
from pathlib import Path

class VideoWebsocketConsumer(AsyncWebsocketConsumer):
    # PosixPath 윈도우 사용불가 -> WindowsPath로 대체
    pathlib.PosixPath = pathlib.WindowsPath

    async def connect(self):
        
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

        await self.channel_layer.group_add(
            "video",
            self.channel_name
        )

    async def disconnect(self, close_code):
        # 방 그룹에서 채널 제거
        await self.channel_layer.group_discard(
            "video",
            self.channel_name
        )

    async def receive(self, bytes_data=None):
        """
        WebSocket으로 이미지 데이터를 수신하여 YOLO 모델로 분석
        """
        if bytes_data:
            try:
                # 이미지를 PIL 형식으로 변환
                image = Image.open(io.BytesIO(bytes_data))

                # YOLO 모델 분석
                result = self.process_image(image)

                # 분석 결과 전송
                await self.send(json.dumps(result))
            except Exception as e:
                # 오류 발생 시 메시지 출력
                error_message = {"error": f"Error processing image: {str(e)}"}
                await self.send(json.dumps(error_message))

    def process_image(self, image):
        # YOLO 모델로 이미지를 분석하고 결과 반환
        image_array = np.array(image)

        # 모델로 예측
        seat_belt_results = self.seat_belt_model(image_array)
        drowsy_results = self.drowsy_model(image_array)

        # 로그 출력
        print("Seat Belt Detection Results:", seat_belt_results.pandas().xyxy[0])
        print("Drowsy Detection Results:", drowsy_results.pandas().xyxy[0])

        # YOLO 감지 결과 처리
        seat_belt_detected = any(seat_belt_results.pandas().xyxy[0]["name"] == "seat_belt")
        drowsy_detected = not any(name in ["Leye", "Reye"] for name in drowsy_results.pandas().xyxy[0].get("name", []))

        # 결과 메시지
        results = {
            "seat_belt": "안전벨트를 착용했습니다." if seat_belt_detected else "안전벨트를 착용하지 않았습니다.",
            "drowsy": "졸음운전이 감지되었습니다. 주의하세요!" if drowsy_detected else "졸음운전이 감지되지 않았습니다."
        }
        return results