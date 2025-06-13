from django.shortcuts import render

# api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import fetch_and_analyze

class SentimentAPIView(APIView):
    """
    GET /api/sentiment/?subreddit=python&limit=50
    or GET /api/sentiment/?keyword=openAI&limit=50
    POST JSON: {"subreddit": "...", "limit": 50} or {"keyword": "...", "limit": 50}
    """
    def get(self, request):
        sub = request.query_params.get('subreddit')
        kw = request.query_params.get('keyword')
        limit_param = request.query_params.get('limit', 100)
        try:
            limit = int(limit_param)
            if limit <= 0 or limit > 500:
                limit = 100
        except ValueError:
            limit = 100

        if not sub and not kw:
            return Response(
                {"error": "Provide 'subreddit' or 'keyword' as query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = fetch_and_analyze(subreddit=sub, keyword=kw, limit=limit)
            return Response({"data": data})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        sub = request.data.get('subreddit')
        kw = request.data.get('keyword')
        limit_param = request.data.get('limit', 100)
        try:
            limit = int(limit_param)
            if limit <= 0 or limit > 500:
                limit = 100
        except ValueError:
            limit = 100

        if not sub and not kw:
            return Response(
                {"error": "Provide 'subreddit' or 'keyword' in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = fetch_and_analyze(subreddit=sub, keyword=kw, limit=limit)
            return Response({"data": data})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
