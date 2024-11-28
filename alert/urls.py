from django.urls import path
from . import views
urlpatterns = [
    path('save/', views.save_alert, name='save_alert'),
]