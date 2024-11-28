import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import AlertEvent

@csrf_exempt
def save_alert(request):
    if request.method == "POST":
        try:
            # 요청 본문에서 JSON 데이터 읽기
            data = json.loads(request.body)
            duration = data.get("duration", 0)  # duration 값을 가져옴 (기본값: 0)

            # AlertEvent 모델에 데이터 저장
            AlertEvent.objects.create(duration=duration)

            # 응답 반환
            return JsonResponse({"message": "Alert saved successfully!"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # POST 요청이 아닌 경우
    return JsonResponse({"error": "Only POST method is allowed."}, status=405)