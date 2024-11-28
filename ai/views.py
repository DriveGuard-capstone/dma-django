import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def process_data(request):
    if request.method == "POST":
        try:
            # JSON 데이터 읽기
            data = json.loads(request.body)

            # 데이터 처리 로직 (예: 예측 모델 실행 등)
            prediction = "safe"  # 예시 값, 실제 예측 로직을 추가

            result = {"status": "success", "prediction": prediction}
            return JsonResponse(result)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)
