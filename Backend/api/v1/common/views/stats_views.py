# api/v1/common/views/stats_views.py

"""
📈 VIEWS DE ESTADÍSTICAS - MÉTRICAS DEL SISTEMA

Views especializadas para generación de estadísticas:
- Métricas generales del sistema
- Análisis de actividad por períodos
- Estadísticas por usuarios y roles
- Comparaciones entre períodos

Casos de uso implementados:
- CU-CM04: Estadísticas generales del sistema
- CU-CM05: Análisis de actividad por períodos
- CU-CM06: Estadísticas por usuario y rol
"""

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..services import StatsService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class StatsView(AuditMixin, PermissionMixin, IPMixin, APIView):
    """
    CU-CM04, CU-CM05, CU-CM06: Vista para estadísticas del sistema.
    
    Endpoint especializado para métricas y análisis:
    - Estadísticas generales del sistema
    - Comparaciones entre períodos
    - Análisis por usuarios y roles
    - Solo para administradores y supervisores
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Stats"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas generales del sistema",
        responses={
            200: openapi.Response(
                description='Estadísticas del sistema',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resumen_general': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'total_registros': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'registros_hoy': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'registros_semana': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'registros_mes': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'usuarios_activos': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'acciones_populares': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                ),
                        'tendencias': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        tags=['Estadísticas']
    )
    def get(self, request):
        """
        CU-CM04: Obtener estadísticas generales del sistema.
        """
        try:
            # Usar servicio para obtener estadísticas
            stats = StatsService.get_system_overview_stats()
            
            # Auditoría
            self.log_audit_action("Consulta estadísticas generales del sistema")
            
            return Response({
                'fecha_consulta': request._request.META.get('HTTP_DATE', ''),
                'usuario_consulta': request.user.username,
                'estadisticas': stats
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas de actividad por usuario",
        operation_id='stats_users',
        manual_parameters=[
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
                description='Estadísticas por usuario',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'usuario': openapi.Schema(type=openapi.TYPE_OBJECT),
                            'actividad': openapi.Schema(type=openapi.TYPE_OBJECT)
                        }
                    )
                )
            )
        },
        tags=['Estadísticas']
    )
    def get_user_stats(self, request):
        """
        CU-CM06: Obtener estadísticas de actividad por usuario.
        """
        try:
            days = int(request.query_params.get('days', 30))
            days = min(days, 365)  # Máximo 1 año
            
            # Usar servicio para obtener estadísticas por usuario
            user_stats = StatsService.get_user_activity_stats(days)
            
            # Auditoría
            self.log_audit_action(f"Consulta estadísticas por usuario - {days} días")
            
            return Response({
                'periodo_dias': days,
                'total_usuarios': len(user_stats),
                'estadisticas_por_usuario': user_stats
            })
            
        except ValueError:
            return Response(
                {'error': 'El parámetro days debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas por usuario: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Comparar estadísticas entre períodos",
        operation_id='stats_comparison',
        manual_parameters=[
            openapi.Parameter(
                'period1_days',
                openapi.IN_QUERY,
                description="Días del período reciente (por defecto 7)",
                type=openapi.TYPE_INTEGER,
                default=7
            ),
            openapi.Parameter(
                'period2_days',
                openapi.IN_QUERY,
                description="Días del período anterior (por defecto 14)",
                type=openapi.TYPE_INTEGER,
                default=14
            )
        ],
        responses={
            200: openapi.Response(
                description='Comparación de períodos',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'periodo_actual': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'periodo_anterior': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'cambios': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        tags=['Estadísticas']
    )
    def get_period_comparison(self, request):
        """
        CU-CM05: Comparar estadísticas entre dos períodos.
        """
        try:
            period1_days = int(request.query_params.get('period1_days', 7))
            period2_days = int(request.query_params.get('period2_days', 14))
            
            # Validar parámetros
            period1_days = min(period1_days, 90)  # Máximo 3 meses
            period2_days = min(period2_days, 180)  # Máximo 6 meses
            
            # Usar servicio para comparar períodos
            comparison = StatsService.get_period_comparison_stats(
                period1_days, 
                period2_days
            )
            
            # Auditoría
            self.log_audit_action(
                f"Comparación de períodos - P1: {period1_days} días, P2: {period2_days} días"
            )
            
            return Response(comparison)
            
        except ValueError:
            return Response(
                {'error': 'Los parámetros de período deben ser números enteros'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al comparar períodos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas agrupadas por roles",
        operation_id='stats_roles',
        responses={
            200: openapi.Response(
                description='Estadísticas por rol',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total_usuarios': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'usuarios_activos_mes': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_acciones_mes': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'promedio_acciones_por_usuario': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                )
            )
        },
        tags=['Estadísticas']
    )
    def get_role_stats(self, request):
        """
        CU-CM06: Obtener estadísticas agrupadas por roles de usuario.
        """
        try:
            # Usar servicio para obtener estadísticas por rol
            role_stats = StatsService.get_role_based_stats()
            
            # Auditoría
            self.log_audit_action("Consulta estadísticas por roles")
            
            return Response({
                'fecha_consulta': request._request.META.get('HTTP_DATE', ''),
                'estadisticas_por_rol': role_stats,
                'resumen': {
                    'total_roles_analizados': len(role_stats),
                    'roles_con_actividad': len([
                        role for role, stats in role_stats.items() 
                        if stats['usuarios_activos_mes'] > 0
                    ])
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas por roles: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Vistas adicionales para endpoints específicos usando decoradores
from django.urls import path
from rest_framework.decorators import api_view, permission_classes

@swagger_auto_schema(
    method='get',
    operation_description="Endpoint directo para estadísticas de usuarios",
    responses={200: "Estadísticas por usuario"}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def user_stats_endpoint(request):
    """Endpoint directo para estadísticas por usuario"""
    view = StatsView()
    view.request = request
    return view.get_user_stats(request)

@swagger_auto_schema(
    method='get', 
    operation_description="Endpoint directo para comparación de períodos",
    responses={200: "Comparación de períodos"}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def period_comparison_endpoint(request):
    """Endpoint directo para comparación de períodos"""
    view = StatsView()
    view.request = request
    return view.get_period_comparison(request)

@swagger_auto_schema(
    method='get',
    operation_description="Endpoint directo para estadísticas por roles", 
    responses={200: "Estadísticas por rol"}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def role_stats_endpoint(request):
    """Endpoint directo para estadísticas por roles"""
    view = StatsView()
    view.request = request
    return view.get_role_stats(request)
