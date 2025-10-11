from api.users.user.serializer import UserSerializer
from rest_framework import serializers
from .models import Bitacora

class BitacoraSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Bitacora
        fields = ['id', 'ip_address', 'user', 'action', 'timestamp']
        read_only_fields = ['id']
