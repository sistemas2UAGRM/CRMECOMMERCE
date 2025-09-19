# api/v1/ecommerce/services/inventory_service.py

"""
📦 SERVICIO DE INVENTARIO - E-COMMERCE

Servicio de negocio para gestión de inventario:
- Control de stock de productos
- Validaciones de disponibilidad
- Actualizaciones de inventario
- Reportes de stock

Principios aplicados:
- Transacciones atómicas para integridad
- Validaciones de negocio centralizadas
- Logging de cambios de stock
"""

from django.db import transaction
from django.db.models import Sum, F
from django.utils import timezone
from core.ecommerce.models import Producto, Stock


class InventoryService:
    """
    Servicio para operaciones de inventario.
    
    Encapsula la lógica de negocio para:
    - Gestión de stock
    - Validaciones de disponibilidad
    - Actualizaciones atómicas
    """
    
    @staticmethod
    def get_product_stock(producto_id):
        """
        Obtener stock actual de un producto.
        
        Args:
            producto_id (int): ID del producto
            
        Returns:
            int: Cantidad disponible en stock
        """
        try:
            stock = Stock.objects.get(producto_id=producto_id)
            return stock.stock_actual
        except Stock.DoesNotExist:
            return 0
    
    @staticmethod
    def check_availability(producto_id, cantidad_solicitada):
        """
        Verificar disponibilidad de stock para un producto.
        
        Args:
            producto_id (int): ID del producto
            cantidad_solicitada (int): Cantidad requerida
            
        Returns:
            dict: {
                'disponible': bool,
                'stock_actual': int,
                'mensaje': str
            }
        """
        stock_actual = InventoryService.get_product_stock(producto_id)
        
        if stock_actual >= cantidad_solicitada:
            return {
                'disponible': True,
                'stock_actual': stock_actual,
                'mensaje': 'Stock disponible'
            }
        else:
            return {
                'disponible': False,
                'stock_actual': stock_actual,
                'mensaje': f'Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad_solicitada}'
            }
    
    @staticmethod
    @transaction.atomic
    def update_stock(producto_id, cantidad, tipo_movimiento='manual', observaciones=''):
        """
        Actualizar stock de un producto de forma atómica.
        
        Args:
            producto_id (int): ID del producto
            cantidad (int): Cantidad a agregar (positivo) o quitar (negativo)
            tipo_movimiento (str): Tipo de movimiento
            observaciones (str): Observaciones del movimiento
            
        Returns:
            dict: Resultado de la operación
            
        Raises:
            Stock.DoesNotExist: Si no existe registro de stock
            ValueError: Si la operación resulta en stock negativo
        """
        try:
            stock = Stock.objects.select_for_update().get(producto_id=producto_id)
            
            nueva_cantidad = stock.stock_actual + cantidad
            
            if nueva_cantidad < 0:
                raise ValueError(f"La operación resultaría en stock negativo: {nueva_cantidad}")
            
            stock.stock_actual = nueva_cantidad
            stock.save()
            
            return {
                'success': True,
                'stock_anterior': stock.stock_actual - cantidad,
                'stock_actual': nueva_cantidad,
                'movimiento': cantidad,
                'mensaje': f'Stock actualizado correctamente'
            }
            
        except Stock.DoesNotExist:
            # Crear registro de stock si no existe
            stock = Stock.objects.create(
                producto_id=producto_id,
                stock_actual=max(0, cantidad),
                stock_min=0
            )
            
            return {
                'success': True,
                'stock_anterior': 0,
                'stock_actual': stock.stock_actual,
                'movimiento': cantidad,
                'mensaje': 'Registro de stock creado'
            }
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """
        Obtener productos con stock bajo.
        
        Args:
            threshold (int): Umbral de stock mínimo
            
        Returns:
            QuerySet: Productos con stock bajo
        """
        return Producto.objects.filter(
            stock__stock_actual__lte=threshold,
            activo=True
        ).select_related('categoria', 'stock').order_by('stock__stock_actual')
    
    @staticmethod
    def get_stock_stats():
        """
        Obtener estadísticas generales de inventario.
        
        Returns:
            dict: Estadísticas de stock
        """
        total_productos = Producto.objects.filter(activo=True).count()
        productos_sin_stock = Producto.objects.filter(
            stock__stock_actual=0,
            activo=True
        ).count()
        productos_bajo_stock = Producto.objects.filter(
            stock__stock_actual__lte=10,
            stock__stock_actual__gt=0,
            activo=True
        ).count()
        
        total_valor_inventario = Stock.objects.aggregate(
            total=Sum(F('stock_actual') * F('producto__precio_venta'))
        )['total'] or 0
        
        return {
            'total_productos': total_productos,
            'productos_sin_stock': productos_sin_stock,
            'productos_bajo_stock': productos_bajo_stock,
            'total_valor_inventario': total_valor_inventario,
            'productos_con_stock': total_productos - productos_sin_stock
        }
    
    @staticmethod
    @transaction.atomic
    def reserve_stock(producto_id, cantidad):
        """
        Reservar stock para una venta (disminuir disponible).
        
        Args:
            producto_id (int): ID del producto
            cantidad (int): Cantidad a reservar
            
        Returns:
            bool: True si se pudo reservar, False si no hay stock
        """
        availability = InventoryService.check_availability(producto_id, cantidad)
        
        if not availability['disponible']:
            return False
        
        result = InventoryService.update_stock(
            producto_id=producto_id,
            cantidad=-cantidad,
            tipo_movimiento='reserva',
            observaciones=f'Reserva de {cantidad} unidades'
        )
        
        return result['success']
    
    @staticmethod
    @transaction.atomic
    def release_stock(producto_id, cantidad):
        """
        Liberar stock reservado (devolver al disponible).
        
        Args:
            producto_id (int): ID del producto
            cantidad (int): Cantidad a liberar
            
        Returns:
            dict: Resultado de la operación
        """
        return InventoryService.update_stock(
            producto_id=producto_id,
            cantidad=cantidad,
            tipo_movimiento='liberacion',
            observaciones=f'Liberación de {cantidad} unidades'
        )
