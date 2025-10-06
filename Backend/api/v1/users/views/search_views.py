# api/v1/users/views/search_views.py

"""
📚 VIEWS DE BÚSQUEDA Y ESTADÍSTICAS

Views especializadas para:
- Búsquedas de usuarios
- Estadísticas del sistema
- Filtros especializados

Casos de uso implementados:
- CU-U05: Búsqueda de Usuarios
- CU-U06: Listar Usuarios Activos  
- CU-U07: Usuarios por Rol
- CU-U08: Estadísticas de Usuarios
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.users.models import User
from ..serializers import UserSearchSerializer, UserStatsSerializer
from ..services import UserManagementService
from ...common.mixins import PermissionMixin, IPMixin


class UserSearchViewSet(PermissionMixin, IPMixin, viewsets.ViewSet):
    """
    ViewSet especializado para búsquedas y estadísticas de usuarios.
    
    Incluye:
    - Búsqueda por término
    - Filtro de usuarios activos
    - Usuarios por rol
    - Estadísticas del sistema
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Buscar usuarios por nombre de usuario o email",
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
                description='Resultados de búsqueda',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'query': openapi.Schema(type=openapi.TYPE_STRING),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'groups': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['Búsqueda de Usuarios']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        CU-U05: Búsqueda de usuarios
        
        Busca usuarios por término en username, email, first_name, last_name.
        Aplica filtros jerárquicos según el rol del usuario.
        """
        query_term = request.query_params.get('q', '').strip()
        
        if not query_term:
            return Response(
                {'error': 'Parámetro de búsqueda "q" es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(query_term) < 2:
            return Response(
                {'error': 'El término de búsqueda debe tener al menos 2 caracteres'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Realizar búsqueda
        users = UserManagementService.search_users(query_term, request.user)
        
        # Serializar resultados
        serializer = UserSearchSerializer(users, many=True)
        
        return Response({
            'query': query_term,
            'count': users.count(),
            'results': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Obtener usuarios activos del sistema",
        responses={
            200: openapi.Response(
                description='Lista de usuarios activos',
                schema=UserSearchSerializer(many=True)
            )
        },
        tags=['Búsqueda de Usuarios']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        CU-U06: Listar usuarios activos
        
        Retorna todos los usuarios con is_active=True.
        Aplica filtros jerárquicos según permisos.
        """
        users = UserManagementService.get_active_users(request.user)
        serializer = UserSearchSerializer(users, many=True)
        
        return Response({
            'count': users.count(),
            'results': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Obtener usuarios por rol específico",
        responses={
            200: openapi.Response(
                description='Usuarios del rol especificado',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'role': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'total_users': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'users': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'rol': openapi.Schema(type=openapi.TYPE_STRING),
                                    'activo': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'fecha_ultimo_acceso': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='Rol no encontrado'
            )
        },
        tags=['Búsqueda de Usuarios']
    )
    @action(detail=False, methods=['get'], url_path='by-role/(?P<role_name>[^/.]+)')
    def by_role(self, request, role_name=None):
        """
        CU-U07: Usuarios por rol
        
        Obtiene usuarios que tienen un rol específico.
        Solo usuarios con permisos apropiados pueden ver esta información.
        """
        # Verificar permisos
        if not self.is_admin_or_supervisor():
            return Response(
                {'error': 'No tienes permisos para ver usuarios por rol'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        result = UserManagementService.get_users_by_role(role_name, request.user)
        
        if 'error' in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        # Serializar usuarios
        users = result['users']
        serializer = UserSearchSerializer(users, many=True)
        
        return Response({
            'role': result['role'],
            'users': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas del sistema de usuarios",
        responses={
            200: openapi.Response(
                description='Estadísticas del sistema',
                schema=UserStatsSerializer
            ),
            403: openapi.Response(
                description='Sin permisos para ver estadísticas'
            )
        },
        tags=['Estadísticas']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        CU-U08: Estadísticas de usuarios
        
        Retorna métricas del sistema:
        - Total de usuarios
        - Usuarios por rol
        - Usuarios activos/inactivos
        - Registros recientes
        - Logins recientes
        """
        # Solo admin y supervisores pueden ver estadísticas completas
        if not self.is_admin_or_supervisor():
            return Response(
                {'error': 'No tienes permisos para ver estadísticas del sistema'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = UserManagementService.get_user_statistics(request.user)
        serializer = UserStatsSerializer(stats)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def roles(self, request):
        """
        Obtener lista de roles disponibles en el sistema.
        """
        if not self.is_employee_or_above():
            return Response(
                {'error': 'No tienes permisos para ver los roles'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.contrib.auth.models import Group
        roles = Group.objects.all().values('id', 'name')
        
        return Response({
            'roles': list(roles),
            'total_roles': len(roles)
        })
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """
        Obtener información jerárquica del usuario actual.
        """
        hierarchy_info = UserManagementService.get_user_hierarchy_info(request.user)
        
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'hierarchy': hierarchy_info
        })

    @swagger_auto_schema(
        operation_description="Obtener lista de empleados del sistema (usuarios con roles de empleado)",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Número de página",
                type=openapi.TYPE_INTEGER,
                default=1
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Término de búsqueda para filtrar empleados",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'active_only',
                openapi.IN_QUERY,
                description="Solo empleados activos",
                type=openapi.TYPE_BOOLEAN,
                default=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Lista paginada de empleados',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'celular': openapi.Schema(type=openapi.TYPE_STRING),
                                    'fecha_de_nacimiento': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                                    'sexo': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                    'groups': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                'name': openapi.Schema(type=openapi.TYPE_STRING)
                                            }
                                        )
                                    )
                                }
                            )
                        )
                    }
                )
            ),
            403: openapi.Response(
                description='Sin permisos para ver empleados'
            )
        },
        tags=['Gestión de Empleados']
    )
    @action(detail=False, methods=['get'])
    def employees(self, request):
        """
        Endpoint específico para obtener empleados del sistema.
        
        Filtra usuarios que tienen roles de empleado (empleadonivel1, empleadonivel2, administrador).
        Incluye paginación y búsqueda.
        """
        # Verificar permisos - solo admin y supervisores pueden ver lista completa de empleados
        if not self.is_admin_or_supervisor():
            return Response(
                {'error': 'No tienes permisos para ver la lista de empleados'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Obtener parámetros de filtro
        active_only_param = request.query_params.get('active_only', None)
        
        # Convertir el parámetro a bool o None
        if active_only_param is None:
            active_only = None  # Mostrar todos
        elif active_only_param.lower() == 'true':
            active_only = True  # Solo activos
        elif active_only_param.lower() == 'false':
            active_only = False  # Solo inactivos
        else:
            active_only = None  # Por defecto, mostrar todos
        
        # Obtener empleados usando el servicio
        result = UserManagementService.get_employees(
            user=request.user,
            search=request.query_params.get('search', ''),
            page=int(request.query_params.get('page', 1)),
            active_only=active_only
        )
        
        return Response(result)
