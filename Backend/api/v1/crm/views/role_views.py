# api/v1/crm/views/role_views.py

"""
👑 VIEWS DE ROLES - CRM

Views especializadas para gestión de roles:
- CRUD completo de roles
- Gestión de permisos por rol
- Consulta de usuarios por rol
- Estadísticas de roles

Casos de uso implementados:
- CU-C01: Gestión de Roles
- CU-C02: Asignación de Permisos a Roles
- CU-C05: Consultar Roles del Sistema
"""

from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.crm.models import RolExtendido
from ..serializers import (
    RolBasicSerializer, RolDetailSerializer, RolPermissionsSerializer,
    UsersByRoleSerializer
)
from ..services import RoleService, PermissionService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class RolViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ModelViewSet):
    """
    CU-C01, CU-C02, CU-C05: Gestión completa de roles.
    
    ViewSet especializado para operaciones de roles:
    - CRUD completo (solo administradores)
    - Gestión de permisos por rol
    - Consultas y estadísticas
    - Usuarios asignados por rol
    """
    
    queryset = RolExtendido.objects.all().order_by('group__name')
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Rol"
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'list':
            return RolBasicSerializer
        elif self.action in ['permissions', 'assign_permissions']:
            return RolPermissionsSerializer
        elif self.action == 'users':
            return UsersByRoleSerializer
        return RolDetailSerializer
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Aplicar filtros según permisos"""
        queryset = super().get_queryset()
        
        # Usar servicio para obtener roles con estadísticas
        return RoleService.get_roles_with_stats()
    
    def perform_create(self, serializer):
        """Crear rol usando servicio de negocio"""
        # Extraer datos del serializer
        name = serializer.validated_data.get('group', {}).get('name', '')
        description = serializer.validated_data.get('descripcion', '')
        
        # Usar servicio para crear rol
        result = RoleService.create_role(
            name=name,
            description=description
        )
        
        if result['success']:
            self.log_audit_action(f"Rol creado: {name}")
            # Retornar el rol creado
            return result['rol']
        else:
            # Si hay error, el serializer manejará la respuesta
            raise serializers.ValidationError(result['error'])
    
    def perform_update(self, serializer):
        """Actualizar rol usando servicio de negocio"""
        instance = serializer.instance
        name = serializer.validated_data.get('group', {}).get('name')
        description = serializer.validated_data.get('descripcion')
        
        # Usar servicio para actualizar
        result = RoleService.update_role(
            role_id=instance.id,
            name=name,
            description=description
        )
        
        if result['success']:
            self.log_audit_action(f"Rol actualizado: {result['rol'].group.name}")
            return result['rol']
        else:
            raise serializers.ValidationError(result['error'])
    
    def perform_destroy(self, instance):
        """Eliminar rol usando servicio de negocio"""
        result = RoleService.delete_role(instance.id)
        
        if result['success']:
            self.log_audit_action(f"Rol eliminado: {instance.group.name}")
        else:
            raise serializers.ValidationError(result['error'])
    
    @swagger_auto_schema(
        operation_description="Obtener permisos asignados a un rol",
        responses={
            200: openapi.Response(
                description='Permisos del rol',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'codename': openapi.Schema(type=openapi.TYPE_STRING),
                            'content_type': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            )
        },
        tags=['Roles']
    )
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """
        CU-C02: Obtener permisos asignados a un rol.
        """
        try:
            rol = self.get_object()
            
            # Usar servicio para obtener permisos
            permissions = RoleService.get_role_permissions(rol.id)
            
            # Serializar permisos
            data = []
            for permission in permissions:
                data.append({
                    'id': permission.id,
                    'name': permission.name,
                    'codename': permission.codename,
                    'content_type': f"{permission.content_type.app_label}.{permission.content_type.model}"
                })
            
            # Auditoría
            self.log_audit_action(f"Consulta permisos del rol: {rol.group.name}")
            
            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener permisos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Asignar permisos a un rol",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'permission_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='Lista de IDs de permisos'
                )
            },
            required=['permission_ids']
        ),
        responses={
            200: openapi.Response(
                description='Permisos asignados exitosamente'
            )
        },
        tags=['Roles']
    )
    @action(detail=True, methods=['post'])
    def assign_permissions(self, request, pk=None):
        """
        CU-C02: Asignar permisos a un rol.
        """
        try:
            rol = self.get_object()
            permission_ids = request.data.get('permission_ids', [])
            
            if not isinstance(permission_ids, list):
                return Response(
                    {'error': 'permission_ids debe ser una lista'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar servicio para asignar permisos
            RoleService._assign_permissions_to_role(rol, permission_ids)
            
            # Auditoría
            self.log_audit_action(f"Permisos asignados al rol: {rol.group.name}")
            
            return Response({
                'mensaje': f'Permisos asignados al rol "{rol.group.name}" exitosamente'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al asignar permisos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener usuarios asignados a un rol",
        responses={
            200: openapi.Response(
                description='Usuarios del rol',
                schema=UsersByRoleSerializer(many=True)
            )
        },
        tags=['Roles']
    )
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        CU-C05: Obtener usuarios asignados a un rol.
        """
        try:
            rol = self.get_object()
            
            # Usar servicio para obtener usuarios
            users = RoleService.get_role_users(rol.id)
            
            # Serializar usuarios
            serializer = UsersByRoleSerializer(users, many=True, context={'request': request})
            
            # Auditoría
            self.log_audit_action(f"Consulta usuarios del rol: {rol.group.name}")
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener usuarios: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Buscar roles por nombre o descripción",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Término de búsqueda",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Roles encontrados',
                schema=RolBasicSerializer(many=True)
            )
        },
        tags=['Roles']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Buscar roles por nombre o descripción.
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Parámetro "q" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar servicio para búsqueda
        roles = RoleService.search_roles(query)
        
        # Serializar resultados
        serializer = RolBasicSerializer(roles, many=True, context={'request': request})
        
        # Auditoría
        self.log_audit_action(f"Búsqueda de roles: '{query}'")
        
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas de roles",
        responses={
            200: openapi.Response(
                description='Estadísticas de roles',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_roles': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'roles_activos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_usuarios_con_roles': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        },
        tags=['Roles']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas generales de roles.
        """
        try:
            from ..services import UserRoleService
            
            # Usar servicio para obtener estadísticas
            stats = UserRoleService.get_role_statistics()
            
            # Auditoría
            self.log_audit_action("Consulta estadísticas de roles")
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
