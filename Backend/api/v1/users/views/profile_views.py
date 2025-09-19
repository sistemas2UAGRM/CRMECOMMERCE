# api/v1/users/views/profile_views.py

"""
📚 VIEWS DE PERFIL DE USUARIO

Views especializadas para gestión de perfil:
- Ver perfil propio
- Actualizar perfil propio
- Validaciones de seguridad

Casos de uso implementados:
- CU-U04: Gestión de Perfil de Usuario
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.users.models import User
from ..serializers import UserDetailSerializer
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class UserProfileViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ViewSet):
    """
    CU-U04: Gestión de perfil de usuario
    
    ViewSet especializado para operaciones de perfil:
    - GET: Ver perfil del usuario actual
    - PUT/PATCH: Actualizar perfil del usuario actual
    - Validaciones de seguridad (solo puede editar su propio perfil)
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Perfil"
    
    @swagger_auto_schema(
        methods=['get'],
        operation_description="Obtener perfil del usuario actual",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description='Perfil del usuario',
                schema=UserDetailSerializer
            )
        },
        tags=['Perfil de Usuario']
    )
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Actualizar perfil del usuario actual",
        security=[{'Bearer': []}],
        request_body=UserDetailSerializer,
        responses={
            200: openapi.Response(
                description='Perfil actualizado exitosamente',
                schema=UserDetailSerializer
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'email': ['Ingrese una dirección de email válida.'],
                        'first_name': ['Este campo no puede estar en blanco.']
                    }
                }
            )
        },
        tags=['Perfil de Usuario']
    )
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Gestionar perfil del usuario actual.
        
        GET: Retorna información del perfil
        PUT/PATCH: Actualiza información del perfil
        """
        user = request.user
        
        if request.method == 'GET':
            return self._get_profile(user)
        elif request.method in ['PUT', 'PATCH']:
            return self._update_profile(request, user)
    
    def _get_profile(self, user):
        """
        Obtener perfil del usuario.
        
        Args:
            user (User): Usuario actual
            
        Returns:
            Response: Datos del perfil
        """
        serializer = UserDetailSerializer(user, context={'request': self.request})
        return Response(serializer.data)
    
    def _update_profile(self, request, user):
        """
        Actualizar perfil del usuario.
        
        Args:
            request: Request object
            user (User): Usuario actual
            
        Returns:
            Response: Perfil actualizado o errores de validación
        """
        partial = request.method == 'PATCH'
        serializer = UserDetailSerializer(
            user, 
            data=request.data, 
            partial=partial,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Validaciones de seguridad adicionales
        validation_error = self._validate_profile_update(serializer.validated_data, user)
        if validation_error:
            return Response(validation_error, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar perfil
        updated_user = serializer.save()
        
        # Auditoría
        self.log_audit_action(f"Perfil actualizado: {updated_user.username}")
        
        # Retornar perfil actualizado
        response_serializer = UserDetailSerializer(updated_user, context={'request': request})
        return Response(response_serializer.data)
    
    def _validate_profile_update(self, validated_data, user):
        """
        Validaciones adicionales para actualización de perfil.
        
        Args:
            validated_data (dict): Datos validados
            user (User): Usuario actual
            
        Returns:
            dict|None: Errores de validación o None si es válido
        """
        # Solo administradores pueden cambiar is_active
        if 'is_active' in validated_data:
            if not self.is_admin(user):
                return {'is_active': ['Solo administradores pueden cambiar el estado activo']}
        
        # Validar cambio de email único
        if 'email' in validated_data:
            new_email = validated_data['email']
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                return {'email': ['Este email ya está en uso por otro usuario']}
        
        # Validar cambio de username único
        if 'username' in validated_data:
            new_username = validated_data['username']
            if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                return {'username': ['Este nombre de usuario ya está en uso']}
        
        return None
    
    @action(detail=False, methods=['get'])
    def permissions(self, request):
        """
        Obtener permisos del usuario actual.
        
        Returns:
            Response: Lista de permisos y roles del usuario
        """
        user = request.user
        
        # Obtener grupos/roles
        groups = list(user.groups.values_list('name', flat=True))
        
        # Obtener permisos específicos
        user_permissions = set()
        for group in user.groups.all():
            user_permissions.update(group.permissions.values_list('codename', flat=True))
        
        # Información jerárquica
        from ..services import UserManagementService
        hierarchy_info = UserManagementService.get_user_hierarchy_info(user)
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'groups': groups,
            'permissions': list(user_permissions),
            'hierarchy': hierarchy_info
        })
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Cambiar contraseña del usuario actual.
        
        Requiere:
        - current_password: Contraseña actual
        - new_password: Nueva contraseña
        - new_password_confirm: Confirmación de nueva contraseña
        """
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        # Validaciones básicas
        if not all([current_password, new_password, new_password_confirm]):
            return Response(
                {'error': 'Todos los campos son requeridos'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != new_password_confirm:
            return Response(
                {'error': 'Las contraseñas nuevas no coinciden'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar contraseña actual
        user = request.user
        if not user.check_password(current_password):
            return Response(
                {'error': 'Contraseña actual incorrecta'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        # Auditoría
        self.log_audit_action(f"Contraseña cambiada: {user.username}")
        
        return Response({'message': 'Contraseña actualizada exitosamente'})
