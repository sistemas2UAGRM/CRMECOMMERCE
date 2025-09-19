# api/v1/ecommerce/views/inventory_views.py

"""
📊 VIEWS DE INVENTARIO - E-COMMERCE

Views especializadas para control de inventario:
- Estadísticas de stock
- Productos con stock bajo
- Reportes de valor de inventario

Casos de uso implementados:
- CU-E04: Consultar Estado de Stock
- CU-E13: Reportes de Inventario
"""

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..services import InventoryService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class InventoryStatsView(AuditMixin, PermissionMixin, IPMixin, APIView):
    """
    CU-E04, CU-E13: Estadísticas y reportes de inventario.
    
    View especializada para operaciones de inventario:
    - Estadísticas generales de stock
    - Productos con stock bajo
    - Reportes de valor de inventario
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Inventario"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas generales de inventario",
        responses={
            200: openapi.Response(
                description='Estadísticas de inventario',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_productos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'productos_con_stock': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'productos_sin_stock': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'valor_total_inventario': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'productos_stock_bajo': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        },
        tags=['Inventario']
    )
    def get(self, request):
        """
        📝 MICROCONCEPTO: Estadísticas de inventario

        Obtiene estadísticas generales del inventario:
        - Total de productos
        - Productos con/sin stock
        - Valor total del inventario
        - Productos con stock bajo
        """
        try:
            # Usar servicio para obtener estadísticas
            stats = InventoryService.get_stock_stats()
            
            # Auditoría
            self.log_audit_action("Consulta estadísticas de inventario")
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LowStockProductsView(AuditMixin, PermissionMixin, IPMixin, APIView):
    """
    CU-E04: Productos con stock bajo
    
    View para consultar productos que necesitan reposición.
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Stock bajo"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Obtener productos con stock bajo",
        manual_parameters=[
            openapi.Parameter(
                'limite', 
                openapi.IN_QUERY, 
                description="Límite de stock (por defecto: stock_min del producto)",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description='Lista de productos con stock bajo',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                            'stock_actual': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'stock_min': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'precio_venta': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'categoria': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            )
        },
        tags=['Inventario']
    )
    def get(self, request):
        """
        📝 MICROCONCEPTO: Alerta de stock bajo

        Identifica productos que necesitan reposición:
        - Stock actual <= stock mínimo configurado
        - Ordenados por criticidad (menor stock primero)
        - Incluye información de precio y categoría
        """
        try:
            # Parámetro opcional de límite
            limite = request.query_params.get('limite')
            if limite:
                limite = int(limite)
            
            # Usar servicio para obtener productos con stock bajo
            productos = InventoryService.get_low_stock_products(limite)
            
            # Auditoría
            self.log_audit_action(f"Consulta productos con stock bajo (límite: {limite or 'automático'})")
            
            return Response(productos)
            
        except ValueError:
            return Response(
                {'error': 'El parámetro "limite" debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al obtener productos con stock bajo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InventoryReportView(AuditMixin, PermissionMixin, IPMixin, APIView):
    """
    CU-E13: Reportes detallados de inventario
    
    View para generar reportes completos de inventario.
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Reporte inventario"
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    @swagger_auto_schema(
        operation_description="Generar reporte detallado de inventario",
        manual_parameters=[
            openapi.Parameter(
                'categoria', 
                openapi.IN_QUERY, 
                description="Filtrar por categoría específica",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'incluir_inactivos', 
                openapi.IN_QUERY, 
                description="Incluir productos inactivos",
                type=openapi.TYPE_BOOLEAN,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description='Reporte detallado de inventario',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'resumen': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'productos': openapi.Schema(type=openapi.TYPE_ARRAY),
                        'por_categoria': openapi.Schema(type=openapi.TYPE_ARRAY)
                    }
                )
            )
        },
        tags=['Inventario']
    )
    def get(self, request):
        """
        📝 MICROCONCEPTO: Reporte completo de inventario

        Genera un reporte detallado que incluye:
        - Resumen general de estadísticas
        - Lista detallada de productos y su stock
        - Análisis por categoría
        - Valor total del inventario
        """
        try:
            # Parámetros de filtro
            categoria_id = request.query_params.get('categoria')
            incluir_inactivos = request.query_params.get('incluir_inactivos', 'false').lower() == 'true'
            
            # Usar servicio para generar reporte
            reporte = InventoryService.generate_inventory_report(
                categoria_id=categoria_id,
                incluir_inactivos=incluir_inactivos
            )
            
            # Auditoría
            filtros = []
            if categoria_id:
                filtros.append(f"categoría: {categoria_id}")
            if incluir_inactivos:
                filtros.append("incluye inactivos")
            
            filtros_str = f" ({', '.join(filtros)})" if filtros else ""
            self.log_audit_action(f"Generó reporte de inventario{filtros_str}")
            
            return Response(reporte)
            
        except Exception as e:
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
