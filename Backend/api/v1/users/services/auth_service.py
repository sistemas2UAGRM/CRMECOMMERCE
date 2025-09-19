# api/v1/users/services/auth_service.py

"""
📚 SERVICIO DE AUTENTICACIÓN

Este servicio encapsula toda la lógica de negocio relacionada
con autenticación, JWT tokens y validaciones de credenciales.

Beneficios:
- Separación de responsabilidades
- Lógica reutilizable
- Testeo independiente
- Facilita cambios futuros (ej: OAuth, 2FA)
"""

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from core.users.models import User


class AuthService:
    """
    Servicio para operaciones de autenticación.
    
    Maneja:
    - Validación de credenciales
    - Generación de tokens JWT
    - Información de usuario para respuesta
    - Asignación de roles por defecto
    """
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Autenticar usuario con email y contraseña.
        
        Args:
            email (str): Email del usuario
            password (str): Contraseña
            
        Returns:
            User: Usuario autenticado o None
            
        Raises:
            serializers.ValidationError: Si las credenciales son inválidas
        """
        # Validar formato de email
        if not email or '@' not in email:
            raise serializers.ValidationError("Email inválido")
        
        # Intentar autenticación
        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        
        if not user.is_active:
            raise serializers.ValidationError("Cuenta desactivada")
        
        return user
    
    @staticmethod
    def generate_tokens(user):
        """
        Generar tokens JWT para usuario.
        
        Args:
            user (User): Usuario autenticado
            
        Returns:
            dict: Diccionario con access_token y refresh_token
        """
        refresh = RefreshToken.for_user(user)
        
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }
    
    @staticmethod
    def get_user_auth_data(user):
        """
        Obtener datos del usuario para respuesta de login.
        
        Args:
            user (User): Usuario autenticado
            
        Returns:
            dict: Datos del usuario (id, username, email, groups, permissions)
        """
        # Obtener grupos del usuario
        groups = list(user.groups.values_list('name', flat=True))
        
        # Obtener permisos del usuario (desde grupos)
        permissions = set()
        for group in user.groups.all():
            permissions.update(group.permissions.values_list('codename', flat=True))
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'groups': groups,
            'permissions': list(permissions)
        }
    
    @staticmethod
    def register_client_user(validated_data):
        """
        Registrar un nuevo usuario cliente.
        
        Args:
            validated_data (dict): Datos validados del serializer
            
        Returns:
            User: Usuario creado
        """
        # Remover campos que no van al modelo
        validated_data.pop('password_confirm', None)
        validated_data.pop('acepta_terminos', None)
        acepta_marketing = validated_data.pop('acepta_marketing', False)
        
        # Crear usuario con contraseña hasheada
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Asignar rol de cliente por defecto
        AuthService.assign_default_client_role(user)
        
        return user
    
    @staticmethod
    def register_admin_user(validated_data):
        """
        Registrar usuario por administrador con rol específico.
        
        Args:
            validated_data (dict): Datos validados del serializer
            
        Returns:
            User: Usuario creado
        """
        rol = validated_data.pop('rol')
        send_welcome_email = validated_data.pop('send_welcome_email', True)
        
        # Generar contraseña temporal si no se proporciona
        password = validated_data.pop('password', None)
        if not password:
            password = User.objects.make_random_password(length=12)
        
        # Crear usuario
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Asignar rol específico
        AuthService.assign_role_to_user(user, rol)
        
        return user
    
    @staticmethod
    def assign_default_client_role(user):
        """
        Asignar rol de cliente por defecto.
        
        Args:
            user (User): Usuario al que asignar el rol
        """
        cliente_group, created = Group.objects.get_or_create(name='cliente')
        user.groups.add(cliente_group)
    
    @staticmethod
    def assign_role_to_user(user, role_name):
        """
        Asignar rol específico a usuario.
        
        Args:
            user (User): Usuario
            role_name (str): Nombre del rol
        """
        group, created = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)
    
    @staticmethod
    def validate_role(role_name):
        """
        Validar que el rol sea válido.
        
        Args:
            role_name (str): Nombre del rol
            
        Returns:
            bool: True si es válido
            
        Raises:
            serializers.ValidationError: Si el rol es inválido
        """
        valid_roles = ['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente']
        
        if role_name not in valid_roles:
            raise serializers.ValidationError(
                f"Rol inválido. Opciones: {', '.join(valid_roles)}"
            )
        
        return True
