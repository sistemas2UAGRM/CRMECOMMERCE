# api/v1/ecommerce/services/cart_service.py

"""
🛒 SERVICIO DE CARRITO - E-COMMERCE

Servicio de negocio para gestión de carrito de compras:
- Operaciones de carrito
- Validaciones de productos
- Cálculos de totales
- Gestión de sesiones

Principios aplicados:
- Transacciones atómicas para consistencia
- Validaciones de stock en tiempo real
- Cálculos automáticos de totales
"""

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, F
from core.ecommerce.models import Carrito, CarritoProducto, Producto
from .inventory_service import InventoryService


class CartService:
    """
    Servicio para operaciones de carrito de compras.
    
    Encapsula la lógica de negocio para:
    - Gestión de productos en carrito
    - Validaciones de disponibilidad
    - Cálculos de totales
    """
    
    @staticmethod
    def get_or_create_cart(user):
        """
        Obtener o crear carrito para un usuario.
        
        Args:
            user: Usuario propietario del carrito
            
        Returns:
            Carrito: Carrito del usuario
        """
        carrito, created = Carrito.objects.get_or_create(
            usuario=user,
            defaults={'estado': 'activo'}
        )
        return carrito
    
    @staticmethod
    @transaction.atomic
    def add_product_to_cart(user, producto_id, cantidad=1):
        """
        Agregar producto al carrito con validaciones.
        
        Args:
            user: Usuario propietario del carrito
            producto_id (int): ID del producto
            cantidad (int): Cantidad a agregar
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar que el producto existe y está activo
            producto = Producto.objects.get(id=producto_id, activo=True)
        except Producto.DoesNotExist:
            return {
                'success': False,
                'error': 'Producto no encontrado o inactivo'
            }
        
        # Validar disponibilidad de stock
        availability = InventoryService.check_availability(producto_id, cantidad)
        if not availability['disponible']:
            return {
                'success': False,
                'error': availability['mensaje']
            }
        
        # Obtener o crear carrito
        carrito = CartService.get_or_create_cart(user)
        
        # Verificar si el producto ya está en el carrito
        carrito_producto, created = CarritoProducto.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            # Si ya existe, sumar cantidad
            nueva_cantidad = carrito_producto.cantidad + cantidad
            
            # Validar stock para la nueva cantidad total
            availability = InventoryService.check_availability(producto_id, nueva_cantidad)
            if not availability['disponible']:
                return {
                    'success': False,
                    'error': f'Stock insuficiente para cantidad total: {availability["mensaje"]}'
                }
            
            carrito_producto.cantidad = nueva_cantidad
            carrito_producto.save()
        
        # Actualizar total del carrito
        CartService._update_cart_total(carrito)
        
        return {
            'success': True,
            'mensaje': f'Producto agregado al carrito',
            'cantidad_total': carrito_producto.cantidad,
            'total_carrito': carrito.total
        }
    
    @staticmethod
    @transaction.atomic
    def update_product_quantity(user, producto_id, nueva_cantidad):
        """
        Actualizar cantidad de un producto en el carrito.
        
        Args:
            user: Usuario propietario del carrito
            producto_id (int): ID del producto
            nueva_cantidad (int): Nueva cantidad
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            carrito = Carrito.objects.get(usuario=user, estado='activo')
            carrito_producto = CarritoProducto.objects.get(
                carrito=carrito,
                producto_id=producto_id
            )
        except (Carrito.DoesNotExist, CarritoProducto.DoesNotExist):
            return {
                'success': False,
                'error': 'Producto no encontrado en el carrito'
            }
        
        if nueva_cantidad <= 0:
            # Eliminar producto del carrito
            carrito_producto.delete()
            CartService._update_cart_total(carrito)
            return {
                'success': True,
                'mensaje': 'Producto eliminado del carrito',
                'total_carrito': carrito.total
            }
        
        # Validar stock para la nueva cantidad
        availability = InventoryService.check_availability(producto_id, nueva_cantidad)
        if not availability['disponible']:
            return {
                'success': False,
                'error': availability['mensaje']
            }
        
        carrito_producto.cantidad = nueva_cantidad
        carrito_producto.save()
        
        # Actualizar total del carrito
        CartService._update_cart_total(carrito)
        
        return {
            'success': True,
            'mensaje': 'Cantidad actualizada',
            'cantidad_total': carrito_producto.cantidad,
            'total_carrito': carrito.total
        }
    
    @staticmethod
    @transaction.atomic
    def remove_product_from_cart(user, producto_id):
        """
        Eliminar producto del carrito.
        
        Args:
            user: Usuario propietario del carrito
            producto_id (int): ID del producto
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            carrito = Carrito.objects.get(usuario=user, estado='activo')
            carrito_producto = CarritoProducto.objects.get(
                carrito=carrito,
                producto_id=producto_id
            )
            carrito_producto.delete()
            
            # Actualizar total del carrito
            CartService._update_cart_total(carrito)
            
            return {
                'success': True,
                'mensaje': 'Producto eliminado del carrito',
                'total_carrito': carrito.total
            }
            
        except (Carrito.DoesNotExist, CarritoProducto.DoesNotExist):
            return {
                'success': False,
                'error': 'Producto no encontrado en el carrito'
            }
    
    @staticmethod
    def get_cart_summary(user):
        """
        Obtener resumen del carrito del usuario.
        
        Args:
            user: Usuario propietario del carrito
            
        Returns:
            dict: Resumen del carrito
        """
        try:
            carrito = Carrito.objects.get(usuario=user, estado='activo')
            productos = CarritoProducto.objects.filter(carrito=carrito).select_related('producto')
            
            items = []
            total_items = 0
            
            for item in productos:
                subtotal = item.cantidad * item.producto.precio_venta
                items.append({
                    'producto_id': item.producto.id,
                    'nombre': item.producto.nombre,
                    'precio_unitario': item.producto.precio_venta,
                    'cantidad': item.cantidad,
                    'subtotal': subtotal
                })
                total_items += item.cantidad
            
            return {
                'carrito_id': carrito.id,
                'items': items,
                'total_items': total_items,
                'total': carrito.total,
                'estado': carrito.estado
            }
            
        except Carrito.DoesNotExist:
            return {
                'carrito_id': None,
                'items': [],
                'total_items': 0,
                'total': Decimal('0.00'),
                'estado': 'vacio'
            }
    
    @staticmethod
    @transaction.atomic
    def clear_cart(user):
        """
        Vaciar carrito del usuario.
        
        Args:
            user: Usuario propietario del carrito
            
        Returns:
            bool: True si se vació correctamente
        """
        try:
            carrito = Carrito.objects.get(usuario=user, estado='activo')
            CarritoProducto.objects.filter(carrito=carrito).delete()
            carrito.total = Decimal('0.00')
            carrito.save()
            return True
        except Carrito.DoesNotExist:
            return True  # No hay carrito, consideramos como "vaciado"
    
    @staticmethod
    def _update_cart_total(carrito):
        """
        Actualizar total del carrito basado en sus productos.
        
        Args:
            carrito (Carrito): Carrito a actualizar
        """
        total = CarritoProducto.objects.filter(carrito=carrito).aggregate(
            total=Sum(F('cantidad') * F('producto__precio_venta'))
        )['total'] or Decimal('0.00')
        
        carrito.total = total
        carrito.save()
    
    @staticmethod
    def validate_cart_stock(user):
        """
        Validar que todos los productos del carrito tengan stock suficiente.
        
        Args:
            user: Usuario propietario del carrito
            
        Returns:
            dict: Resultado de la validación
        """
        try:
            carrito = Carrito.objects.get(usuario=user, estado='activo')
            productos = CarritoProducto.objects.filter(carrito=carrito).select_related('producto')
            
            problemas = []
            
            for item in productos:
                availability = InventoryService.check_availability(
                    item.producto.id, 
                    item.cantidad
                )
                
                if not availability['disponible']:
                    problemas.append({
                        'producto': item.producto.nombre,
                        'cantidad_solicitada': item.cantidad,
                        'stock_disponible': availability['stock_actual'],
                        'mensaje': availability['mensaje']
                    })
            
            return {
                'valido': len(problemas) == 0,
                'problemas': problemas
            }
            
        except Carrito.DoesNotExist:
            return {
                'valido': True,
                'problemas': []
            }
