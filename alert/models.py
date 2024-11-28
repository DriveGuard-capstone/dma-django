from django.db import models

class AlertEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)  # 경고 발생 시간
    duration = models.FloatField()  # 경고 지속 시간 (초)

    def __str__(self):
        return f"Alert at {self.timestamp} ({self.duration}s)"
