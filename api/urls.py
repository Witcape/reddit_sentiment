# api/urls.py

from django.urls import path
from .views import SentimentAPIView

urlpatterns = [
    path('sentiment/', SentimentAPIView.as_view(), name='sentiment_api'),
]
