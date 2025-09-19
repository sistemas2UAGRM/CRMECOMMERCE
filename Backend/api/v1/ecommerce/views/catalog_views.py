# api/v1/ecommerce/views/catalog_views.py

"""
🏪 VIEWS DE CATÁLOGO - E-COMMERCE

Views especializadas para catálogo de productos:
- Gestión de categorías
- Listado de productos por categoría
- Búsquedas en catálogo

Casos de uso implementados:
- CU-E01: Gestión de Categorías
- CU-E06: Consultar Productos por Categoría
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.ecommerce.models import Categoria
from ..serializers import CategoriaBasicSerializer, CategoriaDetailSerializer, ProductoListSerializer
from ..services import CatalogService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class CategoriaViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ModelViewSet):
    """
    CU-E01: Gestión de categorías de productos.
    
    ViewSet especializado para operaciones de catálogo:
    - CRUD de categorías (admin/supervisor)
    - Consulta pública de categorías
    - Productos por categoría
    """
    
    queryset = Categoria.objects.all().order_by('nombre')
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Categoría"
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'list':
            return CategoriaBasicSerializer
        return CategoriaDetailSerializer
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """Auditoría automática en creación"""
        categoria = serializer.save()
        self.log_audit_action(f"Categoría creada: {categoria.nombre}")
    
    def perform_update(self, serializer):
        """Auditoría automática en actualización"""
        categoria = serializer.save()
        self.log_audit_action(f"Categoría actualizada: {categoria.nombre}")
    
    def perform_destroy(self, instance):
        """Auditoría automática en eliminación"""
        self.log_audit_action(f"Categoría eliminada: {instance.nombre}")
        super().perform_destroy(instance)
    
    @swagger_auto_schema(
        operation_description="Obtener productos de una categoría",
        manual_parameters=[
            openapi.Parameter(
                'precio_min',
                openapi.IN_QUERY,
                description="Precio mínimo",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'precio_max',
                openapi.IN_QUERY,
                description="Precio máximo",
                type=openapi.TYPE_NUMBER
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Búsqueda por nombre o descripción",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: openapi.Response(
                description='Productos de la categoría',
                schema=ProductoListSerializer(many=True)
            )
        },
        tags=['Catálogo']
    )
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """
        CU-E06: Obtener productos de una categoría con filtros.
        
        Parámetros de consulta opcionales:
        - precio_min: Filtrar por precio mínimo
        - precio_max: Filtrar por precio máximo
        - search: Búsqueda en nombre/descripción
        """
        try:
            categoria = self.get_object()
            
            # Construir filtros desde query parameters
            filters = {}
            if 'precio_min' in request.query_params:
                try:
                    filters['precio_min'] = float(request.query_params['precio_min'])
                except ValueError:
                    return Response(
                        {'error': 'precio_min debe ser un número válido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if 'precio_max' in request.query_params:
                try:
                    filters['precio_max'] = float(request.query_params['precio_max'])
                except ValueError:
                    return Response(
                        {'error': 'precio_max debe ser un número válido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if 'search' in request.query_params:
                filters['search'] = request.query_params['search']
            
            # Usar servicio para obtener productos filtrados
            productos = CatalogService.get_products_by_category(categoria.id, filters)
            
            # Serializar y retornar
            serializer = ProductoListSerializer(productos, many=True, context={'request': request})
            
            # Auditoría
            self.log_audit_action(f"Consulta productos categoría: {categoria.nombre}")
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener productos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Estadísticas de categorías",
        responses={
            200: openapi.Response(
                description='Estadísticas por categoría',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                            'total_productos': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'productos_activos': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                )
            )
        },
        tags=['Catálogo']
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtener estadísticas de categorías con conteo de productos.
        """
        categorias = CatalogService.get_categories_with_stats()
        
        data = []
        for categoria in categorias:
            data.append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'total_productos': categoria.total_productos,
                'productos_activos': categoria.productos_activos
            })
        
        # Auditoría
        self.log_audit_action("Consulta estadísticas de categorías")
        
        return Response(data)
