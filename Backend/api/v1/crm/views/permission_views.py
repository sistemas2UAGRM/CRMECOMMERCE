# api/v1/crm/views/permission_views.py

"""
🔐 VIEWS DE PERMISOS - CRM

Views especializadas para gestión de permisos:
- Consulta de permisos disponibles
- Permisos por modelo/aplicación
- Búsqueda y filtrado de permisos
- Estadísticas de uso

Casos de uso implementados:
- CU-C03: Consultar Permisos Disponibles
- CU-C02: Gestión de Permisos (lectura)
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..serializers import PermissionSerializer, PermissionDetailSerializer
from ..services import PermissionService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class PermissionViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ReadOnlyModelViewSet):
    """
    CU-C03: Consulta de permisos disponibles en el sistema.
    
    ViewSet de solo lectura para consulta de permisos:
    - Lista de todos los permisos
    - Filtrado por aplicación/modelo
    - Búsqueda por nombre
    - Estadísticas de uso
    """
    
    queryset = Permission.objects.all().select_related('content_type').order_by('content_type__app_label', 'codename')
    serializer_class = PermissionSerializer
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Permiso"
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'retrieve':
            return PermissionDetailSerializer
        return PermissionSerializer
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Aplicar filtros de consulta"""
        queryset = super().get_queryset()
        
        # Filtros opcionales
        app_label = self.request.query_params.get('app')
        model = self.request.query_params.get('model')
        
        if app_label:
            queryset = queryset.filter(content_type__app_label=app_label)
        
        if model:
            queryset = queryset.filter(content_type__model=model)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Listar permisos con auditoría"""
        response = super().list(request, *args, **kwargs)
        
        # Auditoría
        self.log_audit_action("Consulta lista de permisos")
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """Obtener detalle de permiso con auditoría"""
        response = super().retrieve(request, *args, **kwargs)
        
        # Auditoría
        permission = self.get_object()
        self.log_audit_action(f"Consulta detalle permiso: {permission.codename}")
        
        return response
    
    @swagger_auto_schema(
        operation_description="Obtener permisos agrupados por aplicación",
        responses={
            200: openapi.Response(
                description='Permisos agrupados por aplicación',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'codename': openapi.Schema(type=openapi.TYPE_STRING),
                                'model': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    )
                )
            )
        },
        tags=['Permisos']
    )
    @action(detail=False, methods=['get'])
    def by_app(self, request):
        """
        CU-C03: Obtener permisos agrupados por aplicación.
        """
        try:
            # Usar servicio para obtener permisos agrupados
            grouped_permissions = PermissionService.get_permissions_by_app()
            
            # Auditoría
            self.log_audit_action("Consulta permisos agrupados por aplicación")
            
            return Response(grouped_permissions)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener permisos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener permisos de un modelo específico",
        manual_parameters=[
            openapi.Parameter(
                'app_label',
                openapi.IN_QUERY,
                description="Nombre de la aplicación",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'model',
                openapi.IN_QUERY,
                description="Nombre del modelo",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Permisos del modelo',
                schema=PermissionSerializer(many=True)
            )
        },
        tags=['Permisos']
    )
    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """
        CU-C03: Obtener permisos de un modelo específico.
        """
        app_label = request.query_params.get('app_label')
        model = request.query_params.get('model')
        
        if not app_label or not model:
            return Response(
                {'error': 'Parámetros app_label y model son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para obtener permisos del modelo
            permissions = PermissionService.get_model_permissions(app_label, model)
            
            # Serializar
            serializer = PermissionSerializer(permissions, many=True, context={'request': request})
            
            # Auditoría
            self.log_audit_action(f"Consulta permisos del modelo: {app_label}.{model}")
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener permisos del modelo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Buscar permisos por nombre o código",
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
                description='Permisos encontrados',
                schema=PermissionSerializer(many=True)
            )
        },
        tags=['Permisos']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Buscar permisos por nombre o código.
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Parámetro "q" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para búsqueda
            permissions = PermissionService.search_permissions(query)
            
            # Serializar resultados
            serializer = PermissionSerializer(permissions, many=True, context={'request': request})
            
            # Auditoría
            self.log_audit_action(f"Búsqueda de permisos: '{query}'")
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error en búsqueda: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas de permisos",
        responses={
            200: openapi.Response(
                description='Estadísticas de permisos',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_permisos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'permisos_por_app': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER)
                        ),
                        'permisos_mas_usados': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'permission': openapi.Schema(type=openapi.TYPE_STRING),
                                    'usage_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['Permisos']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas de permisos del sistema.
        """
        try:
            # Usar servicio para obtener estadísticas
            stats = PermissionService.get_permission_statistics()
            
            # Auditoría
            self.log_audit_action("Consulta estadísticas de permisos")
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener aplicaciones disponibles",
        responses={
            200: openapi.Response(
                description='Lista de aplicaciones',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'app_label': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'models_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'permissions_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            )
        },
        tags=['Permisos']
    )
    @action(detail=False, methods=['get'])
    def apps(self, request):
        """
        Obtener lista de aplicaciones con información de permisos.
        """
        try:
            # Usar servicio para obtener aplicaciones
            apps_info = PermissionService.get_apps_info()
            
            # Auditoría
            self.log_audit_action("Consulta información de aplicaciones")
            
            return Response(apps_info)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener aplicaciones: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener modelos de una aplicación",
        manual_parameters=[
            openapi.Parameter(
                'app_label',
                openapi.IN_QUERY,
                description="Nombre de la aplicación",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Modelos de la aplicación',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'model': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'permissions_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            )
        },
        tags=['Permisos']
    )
    @action(detail=False, methods=['get'])
    def models(self, request):
        """
        Obtener modelos de una aplicación específica.
        """
        app_label = request.query_params.get('app_label')
        if not app_label:
            return Response(
                {'error': 'Parámetro app_label es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar servicio para obtener modelos
            models_info = PermissionService.get_app_models(app_label)
            
            # Auditoría
            self.log_audit_action(f"Consulta modelos de aplicación: {app_label}")
            
            return Response(models_info)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener modelos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
