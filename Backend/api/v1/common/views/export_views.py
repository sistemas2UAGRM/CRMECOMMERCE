# api/v1/common/views/export_views.py

"""
🔄 VIEWS DE EXPORTACIÓN - GESTIÓN DE DATOS

Views especializadas para exportación de datos:
- Validación de permisos             # Formatear datos según el formato solicitado
            formatted_data = ""
            content_type = "application/json"
            
            if export_format == 'json':
                formatted_data = ExportService.format_as_json(export_data)
                content_type = 'application/json'
            elif export_format == 'csv':
                formatted_data = ExportService.format_as_csv(export_data)
                content_type = 'text/csv'
            elif export_format == 'txt':
                formatted_data = ExportService.format_as_txt(export_data)
                content_type = 'text/plain'
            else:
                # Formato por defecto
                formatted_data = ExportService.format_as_json(export_data)
                content_type = 'application/json'ción
- Múltiples formatos (JSON, CSV, TXT)
- Control de volúmenes de datos
- Metadatos de exportación

Casos de uso implementados:
- CU-CM07: Exportación de datos de bitácora
- CU-CM08: Validación de límites de exportación
- CU-CM09: Formateo en múltiples formatos
"""

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..services import BitacoraService, ExportService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class ExportView(AuditMixin, PermissionMixin, IPMixin, APIView):
    """
    CU-CM07, CU-CM08, CU-CM09: Vista para exportación de datos.
    
    Endpoint especializado para exportar datos de bitácora:
    - Solo administradores pueden exportar
    - Múltiples formatos soportados
    - Validación de límites de volumen
    - Metadatos completos de exportación
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Export"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Exportar datos de bitácora en formato especificado",
        manual_parameters=[
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Formato de exportación (json, csv, txt)",
                type=openapi.TYPE_STRING,
                enum=['json', 'csv', 'txt'],
                default='json'
            ),
            openapi.Parameter(
                'include_sensitive',
                openapi.IN_QUERY,
                description="Incluir datos sensibles (IP, detalles completos)",
                type=openapi.TYPE_BOOLEAN,
                default=False
            ),
            openapi.Parameter(
                'fecha_inicio',
                openapi.IN_QUERY,
                description="Fecha de inicio (ISO format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME
            ),
            openapi.Parameter(
                'fecha_fin',
                openapi.IN_QUERY,
                description="Fecha de fin (ISO format)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME
            ),
            openapi.Parameter(
                'usuario_id',
                openapi.IN_QUERY,
                description="ID del usuario a filtrar",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'accion_contiene',
                openapi.IN_QUERY,
                description="Filtrar por texto en acciones",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description='Datos exportados exitosamente',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'mensaje': openapi.Schema(type=openapi.TYPE_STRING),
                        'formato': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_registros': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'metadatos': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'datos': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(description='Error en parámetros o límites'),
            403: openapi.Response(description='Sin permisos de exportación')
        },
        tags=['Exportación']
    )
    def get(self, request):
        """
        CU-CM07: Exportar datos de bitácora en el formato especificado.
        """
        try:
            # Validar permisos de exportación
            permission_check = ExportService.validate_export_permissions(request.user)
            if not permission_check['valid']:
                return Response(
                    {'error': permission_check['error']},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Obtener parámetros
            export_format = request.query_params.get('format', 'json').lower()
            include_sensitive = request.query_params.get('include_sensitive', 'false').lower() == 'true'
            
            # Validar formato
            if export_format not in ExportService.SUPPORTED_FORMATS:
                return Response(
                    {
                        'error': f'Formato no soportado: {export_format}',
                        'formatos_soportados': ExportService.SUPPORTED_FORMATS
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extraer filtros
            filters = self.extract_filters_from_request(request)
            
            # Obtener queryset con filtros
            base_queryset = BitacoraService.get_user_queryset_by_permissions(request.user)
            filtered_queryset = BitacoraService.apply_advanced_filters(base_queryset, filters)
            
            # Validar tamaño de exportación
            size_check = ExportService.validate_export_size(filtered_queryset.count())
            if not size_check['valid']:
                return Response(
                    {'error': size_check['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Preparar datos para exportación
            export_data = ExportService.prepare_export_data(
                filtered_queryset,
                include_sensitive=include_sensitive
            )
            
            # Generar metadatos
            metadata = ExportService.generate_export_metadata(
                request.user,
                len(export_data),
                filters,
                export_format
            )
            
            # Formatear datos según el formato solicitado
            if export_format == 'json':
                formatted_data = ExportService.format_as_json(export_data, pretty=True)
                content_type = 'application/json'
            elif export_format == 'csv':
                formatted_data = ExportService.format_as_csv(export_data)
                content_type = 'text/csv'
            elif export_format == 'txt':
                formatted_data = ExportService.format_as_txt(export_data)
                content_type = 'text/plain'
            
            # Crear resumen de exportación
            export_summary = ExportService.create_export_summary(export_data, metadata)
            
            # Auditoría
            self.log_audit_action(
                f"Exportación bitácora - Formato: {export_format}, "
                f"Registros: {len(export_data)}, Sensible: {include_sensitive}"
            )
            
            # Decidir si devolver como archivo o JSON con datos
            return_as_file = request.query_params.get('as_file', 'false').lower() == 'true'
            
            if return_as_file:
                # Devolver como archivo descargable
                response = HttpResponse(formatted_data, content_type=content_type)
                filename = f"bitacora_export_{metadata['exportacion']['fecha'][:10]}.{export_format}"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                # Devolver como respuesta JSON con metadatos
                return Response({
                    'mensaje': 'Exportación completada exitosamente',
                    'formato': export_format,
                    'incluye_datos_sensibles': include_sensitive,
                    'resumen': export_summary,
                    'datos_formateados': formatted_data
                })
            
        except Exception as e:
            return Response(
                {'error': f'Error durante la exportación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Validar parámetros de exportación sin realizar la exportación",
        operation_id='validate_export',
        manual_parameters=[
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Formato de exportación a validar",
                type=openapi.TYPE_STRING,
                enum=['json', 'csv', 'txt'],
                default='json'
            ),
            openapi.Parameter(
                'fecha_inicio',
                openapi.IN_QUERY,
                description="Fecha de inicio para estimar volumen",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME
            ),
            openapi.Parameter(
                'fecha_fin',
                openapi.IN_QUERY,
                description="Fecha de fin para estimar volumen",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME
            )
        ],
        responses={
            200: openapi.Response(
                description='Validación de exportación',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valida': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'registros_estimados': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'formato_soportado': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'permisos_validos': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            )
        },
        tags=['Exportación']
    )
    def post(self, request):
        """
        CU-CM08: Validar parámetros de exportación sin realizar la exportación.
        """
        try:
            # Validar permisos
            permission_check = ExportService.validate_export_permissions(request.user)
            
            # Validar formato
            export_format = request.query_params.get('format', 'json').lower()
            format_supported = export_format in ExportService.SUPPORTED_FORMATS
            
            # Estimar volumen de datos
            filters = self.extract_filters_from_request(request)
            base_queryset = BitacoraService.get_user_queryset_by_permissions(request.user)
            filtered_queryset = BitacoraService.apply_advanced_filters(base_queryset, filters)
            estimated_count = filtered_queryset.count()
            
            # Validar tamaño
            size_check = ExportService.validate_export_size(estimated_count)
            
            # Auditoría
            self.log_audit_action(f"Validación exportación - Estimados: {estimated_count} registros")
            
            return Response({
                'validacion': {
                    'valida': (
                        permission_check['valid'] and 
                        format_supported and 
                        size_check['valid']
                    ),
                    'registros_estimados': estimated_count,
                    'formato_soportado': format_supported,
                    'permisos_validos': permission_check['valid'],
                    'tamaño_valido': size_check['valid']
                },
                'detalles': {
                    'permisos': permission_check,
                    'formato': {
                        'solicitado': export_format,
                        'soportados': ExportService.SUPPORTED_FORMATS
                    },
                    'tamaño': size_check
                },
                'filtros_aplicados': filters
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al validar exportación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def extract_filters_from_request(self, request) -> dict:
        """Extraer filtros de los parámetros de consulta"""
        filters = {}
        
        # Lista de filtros soportados para exportación
        filter_params = [
            'fecha_inicio', 'fecha_fin', 'usuario_id', 'accion_contiene',
            'ip', 'objeto_tipo', 'objeto_id', 'detalles_contiene'
        ]
        
        for param in filter_params:
            value = request.query_params.get(param)
            if value:
                filters[param] = value
        
        return filters
