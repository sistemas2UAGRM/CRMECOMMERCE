from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password

import json

class signup(APIView):

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response('Invalid JSON.', status=400)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return Response({'error':'Username, email and password are required.'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'error':'Username already taken.'}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)  # Hash password
        )

        return Response({'message':f"User {user.username} registered successfully."}, status=201)
