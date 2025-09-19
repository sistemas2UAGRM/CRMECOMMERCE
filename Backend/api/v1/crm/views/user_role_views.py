# api/v1/crm/views/user_role_views.py

"""
👥 VIEWS DE ASIGNACIÓN USUARIO-ROL - CRM

Views especializadas para gestión de asignaciones usuario-rol:
- Asignar/desasignar roles a usuarios
- Consultar roles de un usuario
- Gestión masiva de asignaciones
- Historial de cambios

Casos de uso implementados:
- CU-C04: Asignación de Roles a Usuarios
- CU-C06: Gestión de Usuarios en Roles
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.crm.models import RolExtendido
from ..serializers import (
    UserRoleAssignmentSerializer, UserRolesSerializer, 
    RoleUsersSerializer, BulkUserRoleSerializer
)
from ..services import UserRoleService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin

User = get_user_model()


class UserRoleViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ViewSet):
    """
    CU-C04, CU-C06: Gestión de asignaciones usuario-rol.
    
    ViewSet especializado para operaciones de usuario-rol:
    - Asignar/desasignar roles
    - Consultas de asignaciones
    - Operaciones masivas
    - Historial y auditoría
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "AsignacionRol"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Asignar rol a usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del usuario'
                ),
                'role_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del rol'
                )
            },
            required=['user_id', 'role_id']
        ),
        responses={
            200: openapi.Response(description='Rol asignado exitosamente'),
            400: openapi.Response(description='Error en los datos'),
            404: openapi.Response(description='Usuario o rol no encontrado')
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['post'])
    def assign_role(self, request):
        """
        CU-C04: Asignar un rol a un usuario.
        """
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        
        if not user_id or not role_id:
            return Response(
                {'error': 'user_id y role_id son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para asignar rol
            result = UserRoleService.assign_role_to_user(user_id, role_id)
            
            if result['success']:
                # Auditoría
                self.log_audit_action(
                    f"Rol asignado: Usuario {result['user'].username} -> Rol {result['role'].group.name}"
                )
                
                return Response({
                    'mensaje': result['mensaje'],
                    'user': {
                        'id': result['user'].id,
                        'username': result['user'].username
                    },
                    'role': {
                        'id': result['role'].id,
                        'name': result['role'].group.name
                    }
                })
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error al asignar rol: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Desasignar rol de usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del usuario'
                ),
                'role_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del rol'
                )
            },
            required=['user_id', 'role_id']
        ),
        responses={
            200: openapi.Response(description='Rol desasignado exitosamente'),
            400: openapi.Response(description='Error en los datos'),
            404: openapi.Response(description='Usuario o rol no encontrado')
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['post'])
    def remove_role(self, request):
        """
        CU-C04: Desasignar un rol de un usuario.
        """
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        
        if not user_id or not role_id:
            return Response(
                {'error': 'user_id y role_id son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para desasignar rol
            result = UserRoleService.remove_role_from_user(user_id, role_id)
            
            if result['success']:
                # Auditoría
                self.log_audit_action(
                    f"Rol desasignado: Usuario {result['user'].username} <- Rol {result['role'].group.name}"
                )
                
                return Response({
                    'mensaje': result['mensaje']
                })
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Error al desasignar rol: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener roles de un usuario",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                description="ID del usuario",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Roles del usuario',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            )
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/roles')
    def user_roles(self, request, user_id=None):
        """
        CU-C04: Obtener roles asignados a un usuario.
        """
        try:
            # Usar servicio para obtener roles del usuario
            user_roles = UserRoleService.get_user_roles(user_id)
            
            # Preparar respuesta
            roles_data = []
            for role in user_roles:
                roles_data.append({
                    'id': role.id,
                    'name': role.group.name,
                    'description': role.descripcion or ''
                })
            
            # Auditoría
            self.log_audit_action(f"Consulta roles del usuario ID: {user_id}")
            
            return Response(roles_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener roles del usuario: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener usuarios de un rol",
        manual_parameters=[
            openapi.Parameter(
                'role_id',
                openapi.IN_PATH,
                description="ID del rol",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Usuarios del rol',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            )
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['get'], url_path='role/(?P<role_id>[^/.]+)/users')
    def role_users(self, request, role_id=None):
        """
        CU-C06: Obtener usuarios asignados a un rol.
        """
        try:
            # Usar servicio para obtener usuarios del rol
            role_users = UserRoleService.get_role_users(role_id)
            
            # Preparar respuesta
            users_data = []
            for user in role_users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': f"{user.first_name} {user.last_name}".strip()
                })
            
            # Auditoría
            self.log_audit_action(f"Consulta usuarios del rol ID: {role_id}")
            
            return Response(users_data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener usuarios del rol: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Asignación masiva de roles",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='Lista de IDs de usuarios'
                ),
                'role_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del rol a asignar'
                )
            },
            required=['user_ids', 'role_id']
        ),
        responses={
            200: openapi.Response(
                description='Resultado de asignación masiva',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'exitosos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'fallidos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'errores': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            )
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        """
        CU-C06: Asignación masiva de rol a múltiples usuarios.
        """
        user_ids = request.data.get('user_ids', [])
        role_id = request.data.get('role_id')
        
        if not user_ids or not role_id:
            return Response(
                {'error': 'user_ids y role_id son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return Response(
                {'error': 'user_ids debe ser una lista'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para asignación masiva
            result = UserRoleService.bulk_assign_role(user_ids, role_id)
            
            # Auditoría
            self.log_audit_action(
                f"Asignación masiva - Rol ID: {role_id}, "
                f"Exitosos: {result['exitosos']}, Fallidos: {result['fallidos']}"
            )
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'Error en asignación masiva: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Remoción masiva de roles",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='Lista de IDs de usuarios'
                ),
                'role_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del rol a remover'
                )
            },
            required=['user_ids', 'role_id']
        ),
        responses={
            200: openapi.Response(
                description='Resultado de remoción masiva',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'exitosos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'fallidos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'errores': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            )
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['post'])
    def bulk_remove(self, request):
        """
        CU-C06: Remoción masiva de rol de múltiples usuarios.
        """
        user_ids = request.data.get('user_ids', [])
        role_id = request.data.get('role_id')
        
        if not user_ids or not role_id:
            return Response(
                {'error': 'user_ids y role_id son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(user_ids, list):
            return Response(
                {'error': 'user_ids debe ser una lista'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para remoción masiva
            result = UserRoleService.bulk_remove_role(user_ids, role_id)
            
            # Auditoría
            self.log_audit_action(
                f"Remoción masiva - Rol ID: {role_id}, "
                f"Exitosos: {result['exitosos']}, Fallidos: {result['fallidos']}"
            )
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'Error en remoción masiva: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas de asignaciones",
        responses={
            200: openapi.Response(
                description='Estadísticas de asignaciones',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_asignaciones': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'usuarios_con_roles': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'usuarios_sin_roles': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'roles_activos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'promedio_roles_por_usuario': openapi.Schema(type=openapi.TYPE_NUMBER)
                    }
                )
            )
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas de asignaciones usuario-rol.
        """
        try:
            # Usar servicio para obtener estadísticas
            stats = UserRoleService.get_assignment_statistics()
            
            # Auditoría
            self.log_audit_action("Consulta estadísticas de asignaciones usuario-rol")
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Validar asignación de rol",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="ID del usuario",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'role_id',
                openapi.IN_QUERY,
                description="ID del rol",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Resultado de validación',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'tiene_rol': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'puede_asignar': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'restricciones': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            )
        },
        tags=['Asignaciones Usuario-Rol']
    )
    @action(detail=False, methods=['get'])
    def validate_assignment(self, request):
        """
        Validar si se puede asignar un rol a un usuario.
        """
        user_id = request.query_params.get('user_id')
        role_id = request.query_params.get('role_id')
        
        if not user_id or not role_id:
            return Response(
                {'error': 'user_id y role_id son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para validar asignación
            validation = UserRoleService.validate_role_assignment(user_id, role_id)
            
            # Auditoría
            self.log_audit_action(f"Validación asignación - Usuario: {user_id}, Rol: {role_id}")
            
            return Response(validation)
            
        except Exception as e:
            return Response(
                {'error': f'Error al validar asignación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
