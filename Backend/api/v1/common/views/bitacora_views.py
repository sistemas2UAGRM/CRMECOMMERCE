# api/v1/common/views/bitacora_views.py

"""
📊 VIEWS DE BITÁCORA - AUDITORÍA DEL SISTEMA

Views especializadas para gestión de bitácora:
- Consulta con filtros avanzados
- Control de acceso por roles jerárquicos
- Optimizaciones para grandes volúmenes
- Búsqueda y filtrado inteligente

Casos de uso implementados:
- CU-CM01: Consulta de registros de auditoría
- CU-CM02: Filtrado avanzado de bitácora
- CU-CM03: Control de acceso por permisos
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.common.models import Bitacora
from ..serializers import (
    BitacoraListSerializer, BitacoraDetailSerializer,
    BitacoraFilterSerializer
)
from ..services import BitacoraService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class BitacoraViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ReadOnlyModelViewSet):
    """
    CU-CM01, CU-CM02, CU-CM03: Gestión completa de consulta de bitácora.
    
    ViewSet de solo lectura para auditoría del sistema:
    - Lista paginada con filtros avanzados
    - Detalle de registros individuales
    - Control de acceso jerárquico por roles
    - Optimizaciones para performance
    """
    
    queryset = Bitacora.objects.select_related('usuario').order_by('-fecha')
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha', 'accion', 'usuario__username']
    ordering = ['-fecha']  # Por defecto, más recientes primero
    audit_action_prefix = "Bitacora"
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'list':
            return BitacoraListSerializer
        return BitacoraDetailSerializer
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Aplicar filtros según permisos del usuario"""
        # Usar servicio para obtener queryset filtrado por permisos
        return BitacoraService.get_user_queryset_by_permissions(self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Lista con filtros personalizados y auditoría"""
        # Aplicar filtros personalizados usando el servicio
        filters = self.extract_filters_from_request(request)
        queryset = BitacoraService.apply_advanced_filters(
            self.get_queryset(), 
            filters
        )
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            
            # Auditoría de consulta
            self.log_audit_action(
                f"Consulta bitácora - Filtros: {list(filters.keys())} - "
                f"Resultados: {queryset.count()}"
            )
            
            return self.get_paginated_response(serializer.data)
        
        # Sin paginación (no recomendado para bitácora)
        serializer = self.get_serializer(queryset, many=True)
        
        # Auditoría
        self.log_audit_action(f"Consulta bitácora completa - Resultados: {queryset.count()}")
        
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """Detalle de registro con auditoría"""
        response = super().retrieve(request, *args, **kwargs)
        
        # Auditoría
        bitacora = self.get_object()
        self.log_audit_action(f"Consulta detalle bitácora ID: {bitacora.id}")
        
        return response
    
    @swagger_auto_schema(
        operation_description="Obtener actividad reciente del usuario o su equipo",
        manual_parameters=[
            openapi.Parameter(
                'hours',
                openapi.IN_QUERY,
                description="Horas hacia atrás (por defecto 24)",
                type=openapi.TYPE_INTEGER,
                default=24
            )
        ],
        responses={
            200: openapi.Response(
                description='Actividad reciente',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'usuario': openapi.Schema(type=openapi.TYPE_STRING),
                            'accion': openapi.Schema(type=openapi.TYPE_STRING),
                            'fecha': openapi.Schema(type=openapi.TYPE_STRING),
                            'tiempo_transcurrido': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                )
            )
        },
        tags=['Bitácora']
    )
    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        """
        Obtener actividad reciente según permisos del usuario.
        """
        try:
            hours = int(request.query_params.get('hours', 24))
            hours = min(hours, 168)  # Máximo 1 semana
            
            # Usar servicio para obtener actividad reciente
            activity = BitacoraService.get_recent_activity(request.user, hours)
            
            # Auditoría
            self.log_audit_action(f"Consulta actividad reciente - {hours} horas")
            
            return Response({
                'periodo_horas': hours,
                'total_registros': len(activity),
                'actividad': activity
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener actividad reciente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Buscar en registros de auditoría",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Término de búsqueda",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'fields',
                openapi.IN_QUERY,
                description="Campos donde buscar (separados por coma)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description='Resultados de búsqueda',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'usuario': openapi.Schema(type=openapi.TYPE_STRING),
                            'accion': openapi.Schema(type=openapi.TYPE_STRING),
                            'relevancia': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                )
            )
        },
        tags=['Bitácora']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Búsqueda avanzada en registros de auditoría.
        """
        search_term = request.query_params.get('q')
        if not search_term:
            return Response(
                {'error': 'Parámetro "q" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Campos donde buscar
        fields_param = request.query_params.get('fields', '')
        if fields_param:
            search_fields = [f.strip() for f in fields_param.split(',')]
        else:
            search_fields = ['accion', 'detalles', 'usuario__username']
        
        try:
            # Usar servicio para búsqueda
            results = BitacoraService.search_audit_logs(
                request.user, 
                search_term, 
                search_fields
            )
            
            # Auditoría
            self.log_audit_action(
                f"Búsqueda en bitácora: '{search_term}' - "
                f"Campos: {search_fields} - Resultados: {len(results)}"
            )
            
            return Response({
                'termino_busqueda': search_term,
                'campos_buscados': search_fields,
                'total_resultados': len(results),
                'resultados': results
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error en búsqueda: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener resumen de actividad de un usuario",
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="ID del usuario (opcional, por defecto usuario actual)",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Días hacia atrás (por defecto 30)",
                type=openapi.TYPE_INTEGER,
                default=30
            )
        ],
        responses={
            200: openapi.Response(
                description='Resumen de actividad del usuario',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'usuario': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'estadisticas': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        tags=['Bitácora']
    )
    @action(detail=False, methods=['get'])
    def user_summary(self, request):
        """
        Obtener resumen de actividad de un usuario específico.
        """
        try:
            user_id = request.query_params.get('user_id')
            days = int(request.query_params.get('days', 30))
            days = min(days, 365)  # Máximo 1 año
            
            # Usar servicio para obtener resumen
            summary = BitacoraService.get_user_activity_summary(
                request.user,
                int(user_id) if user_id else None,
                days
            )
            
            if 'error' in summary:
                return Response(
                    {'error': summary['error']},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Auditoría
            target_user = user_id or request.user.id
            self.log_audit_action(f"Consulta resumen actividad usuario ID: {target_user}")
            
            return Response(summary)
            
        except ValueError:
            return Response(
                {'error': 'user_id debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener resumen: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def extract_filters_from_request(self, request) -> dict:
        """Extraer filtros de los parámetros de consulta"""
        filters = {}
        
        # Lista de filtros soportados
        filter_params = [
            'fecha_inicio', 'fecha_fin', 'usuario_id', 'accion_contiene',
            'ip', 'objeto_tipo', 'objeto_id', 'detalles_contiene'
        ]
        
        for param in filter_params:
            value = request.query_params.get(param)
            if value:
                filters[param] = value
        
        return filters


class BitacoraFilterView(AuditMixin, PermissionMixin, IPMixin, APIView):
    """
    CU-CM02: Vista para validar filtros de bitácora.
    
    Endpoint especializado para validar filtros antes de aplicarlos,
    útil para UIs complejas de filtrado.
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "BitacoraFilter"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Validar filtros de búsqueda en bitácora",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'fecha_inicio': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description='Fecha de inicio (ISO format)'
                ),
                'fecha_fin': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description='Fecha de fin (ISO format)'
                ),
                'usuario_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID del usuario'
                ),
                'accion_contiene': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Texto a buscar en acciones'
                ),
                'ip': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Dirección IP'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description='Filtros válidos',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'preview_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: openapi.Response(description='Filtros inválidos')
        },
        tags=['Bitácora']
    )
    def post(self, request):
        """
        Validar filtros de bitácora y obtener preview del resultado.
        """
        serializer = BitacoraFilterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Aplicar filtros para obtener un preview
                base_queryset = BitacoraService.get_user_queryset_by_permissions(request.user)
                filtered_queryset = BitacoraService.apply_advanced_filters(
                    base_queryset,
                    serializer.validated_data
                )
                
                preview_count = filtered_queryset.count()
                
                # Auditoría
                self.log_audit_action(f"Validación filtros bitácora - Resultados: {preview_count}")
                
                return Response({
                    'valid': True,
                    'message': 'Filtros válidos',
                    'preview_count': preview_count,
                    'filters_applied': serializer.validated_data
                })
                
            except Exception as e:
                return Response({
                    'valid': False,
                    'error': f'Error al aplicar filtros: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'valid': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
