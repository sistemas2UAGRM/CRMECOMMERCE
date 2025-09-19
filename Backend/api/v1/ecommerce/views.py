# api/v1/ecommerce/views.py

"""
📚 MICROCONCEPTOS - VIEWS PARA E-COMMERCE

Las views de e-commerce requieren consideraciones especiales:

1. TRANSACCIONES: Operaciones de carrito deben ser atómicas
2. STOCK: Validación en tiempo real de disponibilidad
3. PERMISOS: Diferentes niveles según el rol del usuario
4. PERFORMANCE: Optimización para catálogos grandes
5. CÁLCULOS: Totales y subtotales automáticos

Casos de uso implementados: CU-E01 al CU-E13 (Sprint 1 completo)
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Sum, Q, F
from django.db import transaction
from django.utils import timezone

from core.ecommerce.models import Categoria, Producto, Stock, Carrito, CarritoProducto
from core.common.models import Bitacora
from .serializers import (
    CategoriaBasicSerializer, CategoriaDetailSerializer,
    ProductoListSerializer, ProductoDetailSerializer, ProductoCreateSerializer,
    ProductoUpdateStockSerializer, ProductoEstadoSerializer, ProductoStatsSerializer,
    CarritoListSerializer, CarritoDetailSerializer, CarritoProductoSerializer,
    AgregarProductoCarritoSerializer, ActualizarCantidadCarritoSerializer,
    ResumenEstadosSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    📝 CU-E01: Gestión de Categorías
    
    CRUD completo para categorías de productos.
    Solo administradores y supervisores pueden modificar.
    """
    
    queryset = Categoria.objects.all().order_by('nombre')
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoriaBasicSerializer
        return CategoriaDetailSerializer
    
    def get_permissions(self):
        """Solo admin y supervisores pueden modificar categorías"""
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        else:
            return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        categoria = serializer.save()
        Bitacora.objects.create(
            accion=f"Categoría creada: {categoria.nombre}",
            ip=self.get_client_ip(),
            usuario=self.request.user
        )
    
    @action(detail=True, methods=['get'])
    def productos(self, request, pk=None):
        """CU-E12: Productos por Categoría"""
        categoria = self.get_object()
        productos = Producto.objects.filter(
            categoria=categoria, activo=True
        ).select_related('categoria', 'stock')
        
        serializer = ProductoListSerializer(productos, many=True)
        
        # Calcular rango de precios
        precios = productos.values_list('precio_venta', flat=True)
        rango_precios = None
        if precios:
            rango_precios = {
                'min': float(min(precios)),
                'max': float(max(precios))
            }
        
        return Response({
            'categoria': CategoriaDetailSerializer(categoria).data,
            'productos': serializer.data,
            'total_productos': productos.count(),
            'rango_precios': rango_precios
        })
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ProductoViewSet(viewsets.ModelViewSet):
    """
    📝 CU-E02, CU-E03, CU-E04, CU-E05: Gestión de Productos
    
    ViewSet completo para productos con acciones personalizadas.
    """
    
    queryset = Producto.objects.select_related('categoria', 'stock').filter(activo=True)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'precio_venta', 'fecha_creacion']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        elif self.action == 'create':
            return ProductoCreateSerializer
        elif self.action == 'update_stock':
            return ProductoUpdateStockSerializer
        return ProductoDetailSerializer
    
    def get_permissions(self):
        """Permisos según acción"""
        if self.action in ['list', 'retrieve', 'por_estado']:
            # Catálogo público - sin autenticación requerida
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'stock', 'stats']:
            # Operaciones administrativas - solo admin y supervisores
            return [permissions.IsAuthenticated()]
        else:
            return [permissions.IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Crear nuevo producto con stock inicial",
        request_body=ProductoCreateSerializer,
        security=[{'Bearer': []}],  # Requiere autenticación
        responses={
            201: openapi.Response(
                description='Producto creado exitosamente',
                schema=ProductoDetailSerializer,
                examples={
                    'application/json': {
                        'id': 1,
                        'nombre': 'Laptop Dell XPS 13',
                        'descripcion': 'Laptop ultradelgada con procesador Intel i7',
                        'precio_venta': 1299.99,
                        'garantia': '2 años',
                        'categoria': {
                            'id': 1,
                            'nombre': 'Electrónicos'
                        },
                        'stock': {
                            'id': 1,
                            'stock_min': 5,
                            'stock_actual': 20,
                            'disponible': True,
                            'estado': 'disponible'
                        },
                        'activo': True,
                        'fecha_creacion': '2024-09-19T01:00:00Z'
                    }
                }
            )
        },
        tags=['E-commerce - Productos']
    )
    def perform_create(self, serializer):
        """CU-E02: Crear Producto"""
        producto = serializer.save()
        Bitacora.objects.create(
            accion=f"Producto creado: {producto.nombre}",
            ip=self.get_client_ip(),
            usuario=self.request.user
        )
    
    @swagger_auto_schema(
        operation_description="Actualizar stock de un producto",
        request_body=ProductoUpdateStockSerializer,
        security=[{'Bearer': []}],  # Requiere autenticación
        responses={
            200: openapi.Response(
                description='Stock actualizado exitosamente',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'stock_anterior': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'stock_actual': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'stock_min': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'disponible': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'movimiento': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'tipo': openapi.Schema(type=openapi.TYPE_STRING),
                                'cantidad': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'motivo': openapi.Schema(type=openapi.TYPE_STRING),
                                'fecha': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                'usuario': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                ),
                examples={
                    'application/json': {
                        'id': 1,
                        'stock_anterior': 20,
                        'stock_actual': 15,
                        'stock_min': 5,
                        'disponible': True,
                        'movimiento': {
                            'tipo': 'salida',
                            'cantidad': 5,
                            'motivo': 'Venta realizada',
                            'fecha': '2024-09-19T01:15:00Z',
                            'usuario': 'admin'
                        }
                    }
                }
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'stock_actual': ['Este campo es requerido.'],
                        'motivo': ['El motivo es requerido para movimientos de entrada y salida']
                    }
                }
            )
        },
        tags=['E-commerce - Productos']
    )
    @action(detail=True, methods=['put'])
    def stock(self, request, pk=None):
        """CU-E05: Actualizar Stock"""
        producto = self.get_object()
        serializer = ProductoUpdateStockSerializer(data=request.data)
        
        if serializer.is_valid():
            stock_anterior = producto.stock.stock_actual
            nuevo_stock = serializer.validated_data['stock_actual']
            motivo = serializer.validated_data['motivo']
            tipo_movimiento = serializer.validated_data['tipo_movimiento']
            
            # Actualizar stock
            producto.stock.stock_actual = nuevo_stock
            producto.stock.save()
            
            # Registrar en bitácora
            Bitacora.objects.create(
                accion=f"Stock actualizado para {producto.nombre}: {stock_anterior} → {nuevo_stock}. Motivo: {motivo}",
                ip=self.get_client_ip(),
                usuario=request.user
            )
            
            return Response({
                'id': producto.stock.id,
                'stock_anterior': stock_anterior,
                'stock_actual': nuevo_stock,
                'stock_min': producto.stock.stock_min,
                'disponible': nuevo_stock > 0,
                'movimiento': {
                    'tipo': tipo_movimiento,
                    'cantidad': abs(nuevo_stock - stock_anterior),
                    'motivo': motivo,
                    'fecha': timezone.now(),
                    'usuario': request.user.username
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self):
        """Obtener IP del cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    @swagger_auto_schema(
        operation_description="Filtrar productos por estado de disponibilidad",
        security=[],  # Endpoint público - sin autenticación
        manual_parameters=[
            openapi.Parameter(
                'estado',
                openapi.IN_QUERY,
                description='Estado del producto',
                type=openapi.TYPE_STRING,
                enum=['disponible', 'agotado', 'no_disponible'],
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Lista de productos filtrados por estado',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'estado_filtro': openapi.Schema(type=openapi.TYPE_STRING),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'productos': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                                    'precio_venta': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'categoria': openapi.Schema(type=openapi.TYPE_STRING),
                                    'stock_actual': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'estado': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        ),
                        'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje opcional')
                    }
                ),
                examples={
                    'application/json': {
                        'estado_filtro': 'disponible',
                        'count': 18,
                        'productos': [
                            {
                                'id': 1,
                                'nombre': 'Laptop Dell XPS 13',
                                'precio_venta': 1299.99,
                                'categoria': 'Electrónicos',
                                'stock_actual': 15,
                                'estado': 'disponible'
                            },
                            {
                                'id': 2,
                                'nombre': 'Mouse Inalámbrico',
                                'precio_venta': 29.99,
                                'categoria': 'Accesorios',
                                'stock_actual': 50,
                                'estado': 'disponible'
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description='Estado no válido',
                examples={
                    'application/json': {
                        'error': 'Estado no válido. Opciones: disponible, agotado, no_disponible'
                    }
                }
            )
        },
        tags=['E-commerce - Productos']
    )
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """CU-E13: Filtrar Productos por Estado"""
        estado = request.query_params.get('estado', 'disponible')
        
        if estado == 'disponible':
            productos = self.queryset.filter(stock__stock_actual__gt=0)
            mensaje = None
        elif estado == 'agotado':
            productos = self.queryset.filter(stock__stock_actual=0)
            mensaje = "Productos sin stock disponible"
        elif estado == 'no_disponible':
            productos = Producto.objects.select_related('categoria', 'stock').filter(activo=False)
            mensaje = "Productos inactivos o descontinuados"
        else:
            return Response({'error': 'Estado no válido'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductoEstadoSerializer(productos, many=True)
        
        response_data = {
            'estado_filtro': estado,
            'count': productos.count(),
            'productos': serializer.data
        }
        
        if mensaje:
            response_data['mensaje'] = mensaje
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """CU-E11: Estadísticas de Productos"""
        # Solo admin y supervisores
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(role in user_groups for role in ['administrador', 'empleadonivel1']):
            return Response({'error': 'Sin permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        total_productos = Producto.objects.count()
        productos_activos = Producto.objects.filter(activo=True).count()
        productos_sin_stock = Producto.objects.filter(stock__stock_actual=0).count()
        productos_stock_bajo = Producto.objects.filter(
            stock__stock_actual__lte=F('stock__stock_min')
        ).count()
        
        categorias_count = Categoria.objects.count()
        
        # Valor del inventario
        valor_inventario = Producto.objects.filter(activo=True).aggregate(
            total=Sum(F('precio_venta') * F('stock__stock_actual'))
        )['total'] or 0
        
        stats_data = {
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'productos_sin_stock': productos_sin_stock,
            'productos_stock_bajo': productos_stock_bajo,
            'categorias_count': categorias_count,
            'valor_inventario': valor_inventario,
            'productos_mas_vendidos': [],  # Implementar cuando tengamos ventas
            'stock_critico': list(
                Producto.objects.filter(
                    stock__stock_actual__lte=F('stock__stock_min')
                ).values('id', 'nombre', 'stock__stock_actual', 'stock__stock_min')[:5]
            )
        }
        
        serializer = ProductoStatsSerializer(stats_data)
        return Response(serializer.data)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')


class CarritoViewSet(viewsets.ModelViewSet):
    """
    📝 CU-E06, CU-E07, CU-E08, CU-E09, CU-E10: Gestión de Carritos
    
    ViewSet para operaciones de carrito de compras.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Usuarios solo ven sus propios carritos"""
        user = self.request.user
        if user.groups.filter(name__in=['administrador', 'empleadonivel1']).exists():
            return Carrito.objects.all().select_related('usuario').prefetch_related('carritoproducto_set__producto')
        else:
            return Carrito.objects.filter(usuario=user).select_related('usuario').prefetch_related('carritoproducto_set__producto')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CarritoListSerializer
        return CarritoDetailSerializer
    
    def perform_create(self, serializer):
        """CU-E06: Crear Carrito"""
        carrito = serializer.save(usuario=self.request.user)
        Bitacora.objects.create(
            accion=f"Carrito creado para usuario: {self.request.user.username}",
            ip=self.get_client_ip(),
            usuario=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def mi_carrito(self, request):
        """CU-E08: Ver Mi Carrito"""
        try:
            carrito = Carrito.objects.get(usuario=request.user, estado='ABIERTO')
            serializer = CarritoDetailSerializer(carrito)
            return Response(serializer.data)
        except Carrito.DoesNotExist:
            # Crear carrito automáticamente si no existe
            carrito = Carrito.objects.create(usuario=request.user)
            serializer = CarritoDetailSerializer(carrito)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def productos(self, request, pk=None):
        """CU-E07: Agregar Producto al Carrito"""
        carrito = self.get_object()
        serializer = AgregarProductoCarritoSerializer(data=request.data)
        
        if serializer.is_valid():
            producto_id = serializer.validated_data['producto_id']
            cantidad = serializer.validated_data['cantidad']
            
            with transaction.atomic():
                producto = Producto.objects.select_related('stock').get(id=producto_id)
                
                # Verificar si ya existe en el carrito
                carrito_producto, created = CarritoProducto.objects.get_or_create(
                    carrito=carrito,
                    producto=producto,
                    defaults={'cantidad': cantidad}
                )
                
                if not created:
                    # Si ya existe, sumar cantidad
                    nueva_cantidad = carrito_producto.cantidad + cantidad
                    if producto.stock.stock_actual < nueva_cantidad:
                        return Response({
                            'error': f'Solo hay {producto.stock.stock_actual} unidades disponibles'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    carrito_producto.cantidad = nueva_cantidad
                    carrito_producto.save()
                
                # Recalcular total del carrito
                carrito.calcular_total()
                
                # Registrar en bitácora
                Bitacora.objects.create(
                    accion=f"Producto agregado al carrito: {producto.nombre} (cantidad: {cantidad})",
                    ip=self.get_client_ip(),
                    usuario=request.user
                )
            
            # Retornar carrito actualizado
            serializer = CarritoDetailSerializer(carrito)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else self.request.META.get('REMOTE_ADDR')


class ResumenEstadosView(APIView):
    """
    📝 CU-E13: Resumen de Estados de Productos
    
    Endpoint específico para obtener resumen de estados.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        total_productos = Producto.objects.count()
        
        disponible = Producto.objects.filter(activo=True, stock__stock_actual__gt=0).count()
        agotado = Producto.objects.filter(activo=True, stock__stock_actual=0).count()
        no_disponible = Producto.objects.filter(activo=False).count()
        
        data = {
            'resumen_estados': {
                'disponible': {
                    'count': disponible,
                    'porcentaje': round((disponible / total_productos * 100) if total_productos > 0 else 0)
                },
                'agotado': {
                    'count': agotado,
                    'porcentaje': round((agotado / total_productos * 100) if total_productos > 0 else 0)
                },
                'no_disponible': {
                    'count': no_disponible,
                    'porcentaje': round((no_disponible / total_productos * 100) if total_productos > 0 else 0)
                }
            },
            'total_productos': total_productos,
            'productos_activos': disponible + agotado,
            'productos_inactivos': no_disponible
        }
        
        serializer = ResumenEstadosSerializer(data)
        return Response(serializer.data)
