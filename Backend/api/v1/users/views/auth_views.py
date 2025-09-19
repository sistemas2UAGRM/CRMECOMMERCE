# api/v1/users/views/auth_views.py

"""
📚 VIEWS DE AUTENTICACIÓN

Views especializadas para operaciones de autenticación:
- Registro público de clientes
- Registro por administrador 
- Login con JWT

Casos de uso implementados:
- CU-U01: Registro Público de Clientes
- CU-U02: Registro de Usuarios por Administrador  
- CU-U03: Autenticación con JWT
"""

from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..services import AuthService
from ..serializers import (
    UserRegistrationSerializer,
    AdminUserRegistrationSerializer,
    LoginSerializer,
    UserBasicSerializer,
    UserDetailSerializer
)
from ...common.mixins import AuditMixin, IPMixin


class UserRegistrationView(AuditMixin, IPMixin, CreateAPIView):
    """
    CU-U01: Registro público de clientes
    
    Permite que cualquier persona se registre como cliente.
    - Sin autenticación requerida
    - Rol 'cliente' asignado automáticamente
    - Auditoría automática
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Cliente"
    
    @swagger_auto_schema(
        operation_description="Registro público de clientes",
        request_body=UserRegistrationSerializer,
        security=[],  # Endpoint público
        responses={
            201: openapi.Response(
                description='Usuario registrado exitosamente',
                schema=UserBasicSerializer,
                examples={
                    'application/json': {
                        'id': 5,
                        'username': 'juan.cliente',
                        'email': 'juan@gmail.com',
                        'first_name': 'Juan',
                        'last_name': 'Pérez',
                        'full_name': 'Juan Pérez',
                        'is_active': True,
                        'date_joined': '2024-09-19T01:00:00Z'
                    }
                }
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'username': ['Este campo es requerido.'],
                        'email': ['Ingrese una dirección de email válida.'],
                        'password': ['La contraseña es muy común.']
                    }
                }
            )
        },
        tags=['Autenticación']
    )
    def post(self, request, *args, **kwargs):
        """Crear nuevo cliente"""
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Crear usuario cliente con auditoría"""
        user = AuthService.register_client_user(serializer.validated_data)
        return user


class AdminUserRegistrationView(AuditMixin, IPMixin, CreateAPIView):
    """
    CU-U02: Registro de usuarios por administrador
    
    Permite que administradores creen usuarios con roles específicos.
    - Requiere autenticación (temporalmente público para setup inicial)
    - Rol específico asignado según parámetro
    - Contraseña generada automáticamente si no se proporciona
    """
    
    serializer_class = AdminUserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # TEMPORAL: para setup inicial
    audit_action_prefix = "Usuario por admin"
    
    @swagger_auto_schema(
        operation_description="Registro de usuarios por administrador con roles específicos",
        request_body=AdminUserRegistrationSerializer,
        security=[],  # TEMPORAL: Endpoint público para configuración inicial
        responses={
            201: openapi.Response(
                description='Usuario creado exitosamente por administrador',
                schema=UserDetailSerializer,
                examples={
                    'application/json': {
                        'id': 3,
                        'username': 'supervisor.ventas',
                        'email': 'supervisor@empresa.com',
                        'first_name': 'María',
                        'last_name': 'González',
                        'full_name': 'María González',
                        'is_active': True,
                        'groups': [{'id': 2, 'name': 'empleadonivel1'}],
                        'date_joined': '2024-09-19T01:00:00Z'
                    }
                }
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'rol': ['Rol inválido. Opciones: administrador, empleadonivel1, empleadonivel2, cliente'],
                        'username': ['Ya existe un usuario con este nombre.']
                    }
                }
            )
        },
        tags=['Administración']
    )
    def post(self, request, *args, **kwargs):
        """Crear usuario con rol específico"""
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Crear usuario con rol específico y auditoría"""
        user = AuthService.register_admin_user(serializer.validated_data)
        return user


class LoginView(IPMixin, APIView):
    """
    CU-U03: Autenticación con JWT
    
    Autentica usuarios y retorna tokens JWT.
    - Valida credenciales email/contraseña
    - Retorna access_token y refresh_token
    - Incluye información del usuario y permisos
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Autenticación de usuario con JWT",
        request_body=LoginSerializer,
        security=[],  # Endpoint público
        responses={
            200: openapi.Response(
                description='Autenticación exitosa',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access_token': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Token de acceso JWT'
                        ),
                        'refresh_token': openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            description='Token de renovación JWT'
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Información del usuario autenticado'
                        )
                    }
                ),
                examples={
                    'application/json': {
                        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 1,
                            'username': 'admin',
                            'email': 'admin@empresa.com',
                            'first_name': 'Administrador',
                            'last_name': 'Sistema',
                            'groups': ['administrador'],
                            'permissions': ['add_user', 'change_user', 'delete_user']
                        }
                    }
                }
            ),
            400: openapi.Response(
                description='Error de autenticación',
                examples={
                    'application/json': {
                        'error': 'Credenciales inválidas'
                    }
                }
            )
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Autenticar usuario y retornar tokens JWT.
        
        Flujo:
        1. Validar datos de entrada
        2. Autenticar usuario
        3. Generar tokens JWT
        4. Registrar login en auditoría
        5. Retornar respuesta con tokens y datos del usuario
        """
        # Validar datos de entrada
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Autenticar usuario
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = AuthService.authenticate_user(email, password)
            
            # Generar tokens
            tokens = AuthService.generate_tokens(user)
            
            # Obtener datos del usuario
            user_data = AuthService.get_user_auth_data(user)
            
            # Registrar login en auditoría
            from core.common.models import Bitacora
            Bitacora.objects.create(
                accion=f"Login exitoso: {user.username}",
                ip=self.get_client_ip(),
                usuario=user
            )
            
            # Actualizar último login
            user.last_login = request.META.get('HTTP_DATE') or None
            user.save(update_fields=['last_login'])
            
            return Response({
                **tokens,
                'user': user_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Registrar intento fallido
            from core.common.models import Bitacora
            Bitacora.objects.create(
                accion=f"Login fallido: {email if 'email' in locals() else 'email_desconocido'}",
                ip=self.get_client_ip(),
                usuario=None
            )
            
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
