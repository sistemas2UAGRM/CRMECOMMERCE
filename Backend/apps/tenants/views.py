# backend/apps/tenants/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from .serializers import TenantPublicSerializer, TenantRegisterSerializer
from .models import Client

from rest_framework import status
from rest_framework.generics import CreateAPIView

class TenantInfoView(APIView):
    """
    Devuelve información pública del inquilino actual.
    Útil para que el frontend sepa nombre, logo, etc. antes del login.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        schema = connection.schema_name
        if schema == 'public':
            return Response({'type': 'public', 'message': 'Estás en el dominio principal (Landing Page)'})
        
        # Si estamos en un tenant, obtenemos sus datos
        tenant = request.tenant
        serializer = TenantPublicSerializer(tenant)
        return Response({'type': 'tenant', 'data': serializer.data})
    

class RegisterTenantView(CreateAPIView):
    """
    Crea una nueva tienda (inquilino) y su usuario administrador.
    """
    permission_classes = [AllowAny]
    serializer_class = TenantRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        
        # Construir la URL de redirección para el frontend
        # En desarrollo: http://pepita.20.171.166.152:5173/login
        redirect_url = f"http://{tenant.domains.first().domain}:4000/login"
        
        return Response({
            "message": "Tienda creada exitosamente",
            "redirect_url": redirect_url
        }, status=status.HTTP_201_CREATED)