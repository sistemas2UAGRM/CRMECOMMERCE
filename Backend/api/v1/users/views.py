# api/v1/users/views.py
from rest_framework import viewsets, permissions
from core.users.models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
   """
   API endpoint que permite ver los usuarios
   """
   queryset = User.objects.all().order_by('-date_joined')
   serializer_class = UserSerializer
   permission_classes = [permissions.IsAdminUser]
   