# api/v1/ecommerce/views/product_views.py

"""
📦 VIEWS DE PRODUCTOS - E-COMMERCE

Views especializadas para gestión de productos:
- CRUD de productos
- Gestión de estados
- Búsquedas y filtros
- Estadísticas

Casos de uso implementados:
- CU-E02: Gestión de Productos
- CU-E05: Consultar Productos
- CU-E07: Buscar Productos
- CU-E11: Estadísticas de Productos
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.ecommerce.models import Producto
from ..serializers import (
    ProductoListSerializer, ProductoDetailSerializer, ProductoCreateSerializer,
    ProductoEstadoSerializer, ProductoStatsSerializer
)
from ..services import CatalogService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class ProductoViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ModelViewSet):
    """
    CU-E02, CU-E05, CU-E07: Gestión completa de productos.
    
    ViewSet especializado para operaciones de productos:
    - CRUD completo (admin/supervisor)
    - Consultas públicas
    - Búsquedas avanzadas
    - Gestión de estados
    """
    
    queryset = Producto.objects.all().order_by('-fecha_creacion')
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'precio_venta', 'fecha_creacion']
    audit_action_prefix = "Producto"
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'list':
            return ProductoListSerializer
        elif self.action == 'create':
            return ProductoCreateSerializer
        elif self.action in ['cambiar_estado']:
            return ProductoEstadoSerializer
        elif self.action == 'stats':
            return ProductoStatsSerializer
        return ProductoDetailSerializer
    
    def get_permissions(self):
        """Permisos liberados - acceso público a todas las funciones"""
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        """Aplicar filtros según permisos"""
        # Para Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Producto.objects.none()
            
        queryset = super().get_queryset()
        
        # Usuarios regulares solo ven productos activos
        if not (self.request.user.is_authenticated and 
                hasattr(self.request.user, 'rol') and 
                self.request.user.rol in ['administrador', 'empleadonivel1']):
            queryset = queryset.filter(activo=True)
        
        # Filtros adicionales por query parameters
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        precio_min = self.request.query_params.get('precio_min')
        if precio_min:
            try:
                queryset = queryset.filter(precio_venta__gte=float(precio_min))
            except ValueError:
                pass
        
        precio_max = self.request.query_params.get('precio_max')
        if precio_max:
            try:
                queryset = queryset.filter(precio_venta__lte=float(precio_max))
            except ValueError:
                pass
        
        return queryset.select_related('categoria', 'stock')
    
    def perform_create(self, serializer):
        """Auditoría automática en creación"""
        producto = serializer.save()
        self.log_audit_action(f"Producto creado: {producto.nombre}")
    
    def perform_update(self, serializer):
        """Auditoría automática en actualización"""
        producto = serializer.save()
        self.log_audit_action(f"Producto actualizado: {producto.nombre}")
    
    def perform_destroy(self, instance):
        """Auditoría automática en eliminación"""
        self.log_audit_action(f"Producto eliminado: {instance.nombre}")
        super().perform_destroy(instance)
    
    @swagger_auto_schema(
        operation_description="Buscar productos por texto",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description="Término de búsqueda",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'categoria',
                openapi.IN_QUERY,
                description="ID de categoría para filtrar",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description='Productos encontrados',
                schema=ProductoListSerializer(many=True)
            )
        },
        tags=['Productos']
    )
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """
        CU-E07: Búsqueda de productos por texto.
        
        Parámetros requeridos:
        - q: Término de búsqueda
        
        Parámetros opcionales:
        - categoria: ID de categoría para filtrar
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Parámetro "q" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categoria_id = request.query_params.get('categoria')
        
        # Usar servicio para búsqueda
        productos = CatalogService.search_products(query, categoria_id)
        
        # Serializar resultados
        serializer = ProductoListSerializer(productos, many=True, context={'request': request})
        
        # Auditoría
        self.log_audit_action(f"Búsqueda productos: '{query}'")
        
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtener productos populares",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Cantidad máxima de productos (default: 10)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: openapi.Response(
                description='Productos populares',
                schema=ProductoListSerializer(many=True)
            )
        },
        tags=['Productos']
    )
    @action(detail=False, methods=['get'])
    def populares(self, request):
        """
        Obtener productos más populares.
        """
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
        
        # Usar servicio para obtener productos populares
        productos = CatalogService.get_popular_products(limit)
        
        # Serializar resultados
        serializer = ProductoListSerializer(productos, many=True, context={'request': request})
        
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Cambiar estado de un producto",
        request_body=ProductoEstadoSerializer,
        responses={
            200: openapi.Response(
                description='Estado actualizado',
                schema=ProductoDetailSerializer
            )
        },
        tags=['Productos']
    )
    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        """
        Cambiar estado activo/inactivo de un producto.
        """
        producto = self.get_object()
        serializer = ProductoEstadoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        producto.activo = serializer.validated_data['activo']
        producto.save()
        
        estado_texto = "activado" if producto.activo else "desactivado"
        self.log_audit_action(f"Producto {estado_texto}: {producto.nombre}")
        
        response_serializer = ProductoDetailSerializer(producto, context={'request': request})
        return Response(response_serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtener productos agrupados por estado",
        responses={
            200: openapi.Response(
                description='Productos por estado',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'activos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'inactivos': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        },
        tags=['Productos']
    )
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """
        CU-E11: Estadísticas de productos por estado.
        """
        stats = Producto.objects.aggregate(
            activos=Count('id', filter=Q(activo=True)),
            inactivos=Count('id', filter=Q(activo=False)),
            total=Count('id')
        )
        
        # Auditoría
        self.log_audit_action("Consulta estadísticas por estado")
        
        return Response(stats)
    
    @swagger_auto_schema(
        operation_description="Estadísticas generales de productos",
        responses={
            200: openapi.Response(
                description='Estadísticas generales',
                schema=ProductoStatsSerializer
            )
        },
        tags=['Productos']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        CU-E11: Estadísticas generales de productos.
        """
        # Estadísticas básicas
        total_productos = Producto.objects.count()
        productos_activos = Producto.objects.filter(activo=True).count()
        
        # Estadísticas por categoría
        por_categoria = Producto.objects.values('categoria__nombre').annotate(
            total=Count('id')
        ).order_by('-total')[:5]  # Top 5 categorías
        
        # Productos sin stock
        sin_stock = Producto.objects.filter(
            stock__stock_actual=0,
            activo=True
        ).count()
        
        data = {
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'productos_inactivos': total_productos - productos_activos,
            'productos_sin_stock': sin_stock,
            'top_categorias': list(por_categoria)
        }
        
        # Auditoría
        self.log_audit_action("Consulta estadísticas generales de productos")
        
        return Response(data)
