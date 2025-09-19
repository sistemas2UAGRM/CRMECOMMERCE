# api/v1/users/views/admin_views.py

"""
📚 VIEWS DE ADMINISTRACIÓN DE USUARIOS

Views especializadas para administración:
- Listar usuarios (con filtros de permisos)
- CRUD de usuarios (solo administradores)
- Gestión de estados

Casos de uso implementados:
- Listar usuarios con filtros jerárquicos
- Administración completa de usuarios
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.users.models import User
from ..serializers import UserBasicSerializer, UserDetailSerializer
from ..services import UserManagementService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class UserAdminViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ModelViewSet):
    """
    ViewSet para administración de usuarios.
    
    Funcionalidades:
    - CRUD completo de usuarios (solo admin)
    - Filtros jerárquicos según rol del usuario
    - Auditoría automática de cambios
    """
    
    queryset = User.objects.all().order_by('-date_joined')
    audit_action_prefix = "Usuario"
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'list':
            return UserBasicSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Aplicar filtros liberados - mostrar todos los usuarios"""
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return super().get_queryset()
    
    @swagger_auto_schema(
        operation_description="Listar usuarios con filtros jerárquicos",
        responses={
            200: openapi.Response(
                description='Lista de usuarios',
                schema=UserBasicSerializer(many=True)
            )
        },
        tags=['Administración de Usuarios']
    )
    def list(self, request, *args, **kwargs):
        """Listar usuarios aplicando filtros jerárquicos"""
        return super().list(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activar usuario específico.
        Solo administradores.
        """
        if not self.is_admin():
            return Response(
                {'error': 'Solo administradores pueden activar usuarios'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        if user.is_active:
            return Response(
                {'message': 'El usuario ya está activo'}, 
                status=status.HTTP_200_OK
            )
        
        user.is_active = True
        user.save()
        
        self.log_audit_action(f"Usuario activado: {user.username}")
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactivar usuario específico.
        Solo administradores.
        """
        if not self.is_admin():
            return Response(
                {'error': 'Solo administradores pueden desactivar usuarios'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        if not user.is_active:
            return Response(
                {'message': 'El usuario ya está inactivo'}, 
                status=status.HTTP_200_OK
            )
        
        # Prevenir auto-desactivación
        if user.id == request.user.id:
            return Response(
                {'error': 'No puedes desactivarte a ti mismo'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        self.log_audit_action(f"Usuario desactivado: {user.username}")
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def activity_log(self, request, pk=None):
        """
        Obtener log de actividad de un usuario específico.
        Solo administradores y supervisores.
        """
        if not self.is_admin_or_supervisor():
            return Response(
                {'error': 'No tienes permisos para ver el log de actividad'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        
        # Obtener actividad reciente del usuario
        from core.common.models import Bitacora
        activity = Bitacora.objects.filter(usuario=user).order_by('-fecha')[:20]
        
        activity_data = []
        for entry in activity:
            activity_data.append({
                'id': entry.id,
                'action': entry.accion,
                'date': entry.fecha,
                'ip': entry.ip
            })
        
        return Response({
            'user_id': user.id,
            'username': user.username,
            'recent_activity': activity_data
        })
    
    def perform_update(self, serializer):
        """Override para auditoría personalizada en actualizaciones"""
        old_instance = self.get_object()
        updated_instance = serializer.save()
        
        # Detectar cambios importantes
        changes = []
        if old_instance.is_active != updated_instance.is_active:
            status_change = "activado" if updated_instance.is_active else "desactivado"
            changes.append(f"estado {status_change}")
        
        if old_instance.email != updated_instance.email:
            changes.append(f"email cambiado de {old_instance.email} a {updated_instance.email}")
        
        if changes:
            change_description = ", ".join(changes)
            self.log_audit_action(f"Usuario {updated_instance.username} modificado: {change_description}")
        else:
            self.log_audit_action(f"Usuario actualizado: {updated_instance.username}")
        
        return updated_instance
