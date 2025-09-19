# api/v1/ecommerce/views/cart_views.py

"""
🛒 VIEWS DE CARRITO - E-COMMERCE

Views especializadas para carrito de compras:
- Gestión de carrito personal
- Agregar/quitar productos
- Actualizar cantidades
- Validaciones de stock

Casos de uso implementados:
- CU-E08: Gestión de Carrito
- CU-E09: Agregar Productos al Carrito
- CU-E10: Actualizar Cantidad en Carrito
- CU-E12: Consultar Mi Carrito
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.ecommerce.models import Carrito
from ..serializers import (
    CarritoListSerializer, CarritoDetailSerializer,
    AgregarProductoCarritoSerializer, ActualizarCantidadCarritoSerializer
)
from ..services import CartService
from ...common.mixins import AuditMixin, PermissionMixin, IPMixin


class CarritoViewSet(AuditMixin, PermissionMixin, IPMixin, viewsets.ModelViewSet):
    """
    CU-E08, CU-E09, CU-E10, CU-E12: Gestión completa de carrito.
    
    ViewSet especializado para operaciones de carrito:
    - Ver mi carrito actual
    - Agregar productos con validaciones
    - Actualizar cantidades
    - Eliminar productos
    """
    
    permission_classes = [permissions.AllowAny]
    audit_action_prefix = "Carrito"
    
    def get_queryset(self):
        """Solo carritos del usuario actual"""
        # Para Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Carrito.objects.none()
            
        if not self.request.user.is_authenticated:
            return Carrito.objects.none()
            
        return Carrito.objects.filter(usuario=self.request.user)
    
    def get_serializer_class(self):
        """Serializer dinámico según acción"""
        if self.action == 'list':
            return CarritoListSerializer
        elif self.action == 'agregar_producto':
            return AgregarProductoCarritoSerializer
        elif self.action == 'actualizar_cantidad':
            return ActualizarCantidadCarritoSerializer
        return CarritoDetailSerializer
    
    def perform_create(self, serializer):
        """Asignar usuario automáticamente"""
        carrito = serializer.save(usuario=self.request.user)
        self.log_audit_action("Carrito creado")
    
    @swagger_auto_schema(
        operation_description="Obtener mi carrito actual",
        responses={
            200: openapi.Response(
                description='Carrito del usuario',
                schema=CarritoDetailSerializer
            )
        },
        tags=['Carrito']
    )
    @action(detail=False, methods=['get'])
    def mi_carrito(self, request):
        """
        CU-E12: Obtener carrito actual del usuario.
        
        Retorna el carrito activo del usuario con todos sus productos.
        Si no existe carrito, retorna estructura vacía.
        """
        try:
            # Usar servicio para obtener resumen del carrito
            resumen = CartService.get_cart_summary(request.user)
            
            return Response(resumen)
            
        except Exception as e:
            return Response(
                {'error': f'Error al obtener carrito: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Agregar producto al carrito",
        request_body=AgregarProductoCarritoSerializer,
        responses={
            200: openapi.Response(
                description='Producto agregado exitosamente',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'mensaje': openapi.Schema(type=openapi.TYPE_STRING),
                        'cantidad_total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_carrito': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description='Error de validación o stock insuficiente'
            )
        },
        tags=['Carrito']
    )
    @action(detail=False, methods=['post'])
    def agregar_producto(self, request):
        """
        CU-E09: Agregar producto al carrito.
        
        Valida stock disponible antes de agregar.
        Si el producto ya existe, suma la cantidad.
        """
        serializer = AgregarProductoCarritoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar servicio para agregar producto
        result = CartService.add_product_to_cart(
            user=request.user,
            producto_id=serializer.validated_data['producto_id'],
            cantidad=serializer.validated_data.get('cantidad', 1)
        )
        
        if result['success']:
            # Auditoría
            self.log_audit_action(f"Producto agregado al carrito: ID {serializer.validated_data['producto_id']}")
            return Response(result)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Actualizar cantidad de producto en carrito",
        request_body=ActualizarCantidadCarritoSerializer,
        responses={
            200: openapi.Response(
                description='Cantidad actualizada exitosamente'
            ),
            400: openapi.Response(
                description='Error de validación o stock insuficiente'
            )
        },
        tags=['Carrito']
    )
    @action(detail=False, methods=['patch'])
    def actualizar_cantidad(self, request):
        """
        CU-E10: Actualizar cantidad de producto en carrito.
        
        Si la nueva cantidad es 0 o negativa, elimina el producto del carrito.
        Valida stock disponible antes de actualizar.
        """
        serializer = ActualizarCantidadCarritoSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar servicio para actualizar cantidad
        result = CartService.update_product_quantity(
            user=request.user,
            producto_id=serializer.validated_data['producto_id'],
            nueva_cantidad=serializer.validated_data['cantidad']
        )
        
        if result['success']:
            # Auditoría
            self.log_audit_action(f"Cantidad actualizada en carrito: ID {serializer.validated_data['producto_id']}")
            return Response(result)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Eliminar producto del carrito",
        manual_parameters=[
            openapi.Parameter(
                'producto_id',
                openapi.IN_QUERY,
                description="ID del producto a eliminar",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Producto eliminado exitosamente'
            ),
            400: openapi.Response(
                description='Producto no encontrado en carrito'
            )
        },
        tags=['Carrito']
    )
    @action(detail=False, methods=['delete'])
    def eliminar_producto(self, request):
        """
        Eliminar producto específico del carrito.
        """
        producto_id = request.query_params.get('producto_id')
        
        if not producto_id:
            return Response(
                {'error': 'Parámetro producto_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            producto_id = int(producto_id)
        except ValueError:
            return Response(
                {'error': 'producto_id debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar servicio para eliminar producto
        result = CartService.remove_product_from_cart(
            user=request.user,
            producto_id=producto_id
        )
        
        if result['success']:
            # Auditoría
            self.log_audit_action(f"Producto eliminado del carrito: ID {producto_id}")
            return Response(result)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Vaciar carrito completamente",
        responses={
            200: openapi.Response(
                description='Carrito vaciado exitosamente'
            )
        },
        tags=['Carrito']
    )
    @action(detail=False, methods=['delete'])
    def vaciar(self, request):
        """
        Vaciar completamente el carrito del usuario.
        """
        success = CartService.clear_cart(request.user)
        
        if success:
            # Auditoría
            self.log_audit_action("Carrito vaciado")
            return Response({'mensaje': 'Carrito vaciado exitosamente'})
        else:
            return Response(
                {'error': 'Error al vaciar carrito'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Validar stock de productos en carrito",
        responses={
            200: openapi.Response(
                description='Resultado de validación de stock',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valido': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'problemas': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'producto': openapi.Schema(type=openapi.TYPE_STRING),
                                    'cantidad_solicitada': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'stock_disponible': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'mensaje': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            )
        },
        tags=['Carrito']
    )
    @action(detail=False, methods=['get'])
    def validar_stock(self, request):
        """
        Validar que todos los productos del carrito tengan stock suficiente.
        
        Útil antes de proceder al checkout o finalizar compra.
        """
        result = CartService.validate_cart_stock(request.user)
        
        # Auditoría
        self.log_audit_action("Validación de stock de carrito")
        
        return Response(result)
