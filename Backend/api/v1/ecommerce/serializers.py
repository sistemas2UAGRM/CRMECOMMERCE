# api/v1/ecommerce/serializers.py

"""
📚 MICROCONCEPTOS - SERIALIZERS PARA E-COMMERCE

En un sistema de e-commerce, los serializers deben manejar:

1. RELACIONES COMPLEJAS: Productos con categorías, stock, carritos
2. VALIDACIONES DE NEGOCIO: Stock disponible, precios válidos
3. CAMPOS CALCULADOS: Totales, disponibilidad, descuentos
4. OPTIMIZACIÓN: Evitar N+1 queries en listados
5. SEGURIDAD: Filtrar información sensible por rol

Patrones implementados:
- Serializers anidados para relaciones
- Validación de stock en tiempo real
- Cálculos automáticos de totales
- Diferentes niveles de detalle por endpoint
"""

from rest_framework import serializers
from django.db import transaction
from decimal import Decimal

from core.ecommerce.models import Categoria, Producto, Stock, Carrito, CarritoProducto
from core.users.models import User


class CategoriaBasicSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer básico para listados
    
    Para listados de categorías, solo necesitamos información esencial.
    Incluimos un campo calculado para contar productos.
    """
    
    productos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'productos_count']
    
    def get_productos_count(self, obj):
        """
        📝 MICROCONCEPTO: SerializerMethodField para campos calculados
        
        Cuenta productos activos en la categoría.
        En producción, esto debería estar pre-calculado o usar annotations.
        """
        return obj.productos.filter(activo=True).count()


class CategoriaDetailSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer detallado con información completa
    
    Para vistas de detalle, incluimos más información y estadísticas.
    """
    
    productos_count = serializers.SerializerMethodField()
    productos_disponibles = serializers.SerializerMethodField()
    rango_precios = serializers.SerializerMethodField()
    
    class Meta:
        model = Categoria
        fields = [
            'id', 'nombre', 'descripcion', 'productos_count',
            'productos_disponibles', 'rango_precios', 'fecha_creacion'
        ]
    
    def get_productos_count(self, obj):
        return obj.productos.filter(activo=True).count()
    
    def get_productos_disponibles(self, obj):
        """Productos con stock > 0"""
        return obj.productos.filter(
            activo=True,
            stock__stock_actual__gt=0
        ).count()
    
    def get_rango_precios(self, obj):
        """
        📝 MICROCONCEPTO: Agregaciones en SerializerMethodField
        
        Calcula el rango de precios de productos en la categoría.
        """
        productos = obj.productos.filter(activo=True)
        if not productos.exists():
            return None
        
        precios = productos.values_list('precio_venta', flat=True)
        return {
            'min': float(min(precios)),
            'max': float(max(precios))
        }


class StockSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer para entidad relacionada
    
    El stock es una entidad crítica que requiere validaciones especiales.
    """
    
    disponible = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    
    class Meta:
        model = Stock
        fields = ['id', 'stock_min', 'stock_actual', 'disponible', 'estado']
        #fields = ['id', 'stock_min', 'stock_actual']
        read_only_fields = ['id']
    
    def get_disponible(self, obj):
        """Producto disponible si stock > 0"""
        return obj.stock_actual > 0
    
    def get_estado(self, obj):
        """
        📝 MICROCONCEPTO: Lógica de negocio en serializers
        
        Determina el estado del stock según reglas de negocio.
        """
        if obj.stock_actual <= 0:
            return 'agotado'
        elif obj.stock_actual <= obj.stock_min:
            return 'stock_bajo'
        else:
            return 'disponible'
    
    def validate_stock_actual(self, value):
        """
        📝 MICROCONCEPTO: Validación de campo individual
        
        El stock actual no puede ser negativo.
        """
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        return value


class ProductoListSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer optimizado para listados
    
    Para listados de productos, minimizamos la información para mejorar performance.
    Usamos select_related para evitar N+1 queries.
    """
    
    categoria = serializers.CharField(source='categoria.id', read_only=True)
    disponible = serializers.SerializerMethodField()
    stock_disponible = serializers.IntegerField(source='stock.stock_actual', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio_venta', 'categoria', 'descripcion', 
            'disponible', 'stock_disponible'
        ]
    
    def get_disponible(self, obj):
        """Producto disponible si tiene stock y está activo"""
        return obj.activo and hasattr(obj, 'stock') and obj.stock.stock_actual > 0


class ProductoDetailSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer completo para detalles
    
    Incluye toda la información del producto y relaciones anidadas.
    """
    
    categoria = CategoriaBasicSerializer(read_only=True)
    stock = StockSerializer(read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio_venta', 'garantia',
            'categoria', 'stock', 'activo', 'fecha_creacion'
        ]


class ProductoCreateSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer para creación con validaciones
    
    Maneja la creación de productos junto con su stock inicial.
    Usa transacciones para garantizar consistencia.
    """
    
    stock = StockSerializer()
    categoria_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'nombre', 'descripcion', 'precio_venta', 'garantia',
            'categoria_id', 'stock'
        ]
    
    def validate_precio_venta(self, value):
        """
        📝 MICROCONCEPTO: Validación de reglas de negocio
        
        El precio debe ser positivo y tener máximo 2 decimales.
        """
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        
        # Validar máximo 2 decimales
        if value.as_tuple().exponent < -2:
            raise serializers.ValidationError("El precio no puede tener más de 2 decimales")
        
        return value
    
    def validate_categoria_id(self, value):
        """Validar que la categoría existe"""
        try:
            Categoria.objects.get(id=value)
        except Categoria.DoesNotExist:
            raise serializers.ValidationError("La categoría especificada no existe")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """
        📝 MICROCONCEPTO: Creación con transacciones
        
        Crea el producto y su stock en una sola transacción.
        Si algo falla, se revierte todo.
        """
        stock_data = validated_data.pop('stock')
        categoria_id = validated_data.pop('categoria_id')
        
        # Crear stock asociado
        stock = Stock.objects.create( **stock_data)
        
        # Crear producto
        producto = Producto.objects.create(
            stock=stock,
            categoria_id=categoria_id,
            **validated_data
        )
        
        return producto


class ProductoUpdateStockSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para operaciones específicas
    
    Para actualizar stock, usamos un Serializer (no ModelSerializer)
    porque no estamos serializando un modelo directamente.
    """
    
    stock_actual = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField(max_length=200, required=False, default="")
    tipo_movimiento = serializers.ChoiceField(
        choices=[('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste')],
        default='ajuste'
    )
    
    def validate(self, data):
        """
        📝 MICROCONCEPTO: Validación a nivel de objeto
        
        Validaciones que requieren múltiples campos.
        """
        if data['tipo_movimiento'] in ['entrada', 'salida'] and not data['motivo']:
            raise serializers.ValidationError({
                'motivo': 'El motivo es requerido para movimientos de entrada y salida'
            })
        
        return data


class CarritoProductoSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer para relación many-to-many con campos extra
    
    CarritoProducto es la tabla intermedia entre Carrito y Producto.
    Incluye campos adicionales como cantidad.
    """
    
    producto = ProductoListSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CarritoProducto
        fields = ['id', 'producto', 'cantidad', 'subtotal', 'fecha_agregado']
    
    def get_subtotal(self, obj):
        """
        📝 MICROCONCEPTO: Cálculo de subtotal
        
        Subtotal = precio_producto * cantidad
        """
        return float(obj.producto.precio_venta * obj.cantidad)


class CarritoListSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer para listados de carritos
    
    Vista simplificada para listados administrativos.
    """
    
    usuario = serializers.CharField(source='usuario.username', read_only=True)
    items_count = serializers.SerializerMethodField()
    productos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Carrito
        fields = [
            'id', 'usuario', 'estado', 'total', 'items_count', 
            'productos_count', 'fecha_creacion'
        ]
    
    def get_items_count(self, obj):
        """Número de líneas diferentes en el carrito"""
        return obj.carritoproducto_set.count()
    
    def get_productos_count(self, obj):
        """Número total de productos (suma de cantidades)"""
        return sum(
            item.cantidad for item in obj.carritoproducto_set.all()
        )


class CarritoDetailSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer completo para carrito
    
    Incluye todos los productos y cálculos de totales.
    """
    
    usuario = serializers.StringRelatedField(read_only=True)
    productos = CarritoProductoSerializer(source='carritoproducto_set', many=True, read_only=True)
    resumen = serializers.SerializerMethodField()
    
    class Meta:
        model = Carrito
        fields = [
            'id', 'usuario', 'estado', 'total', 'productos', 
            'resumen', 'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def get_resumen(self, obj):
        """
        📝 MICROCONCEPTO: Resumen calculado del carrito
        
        Proporciona información agregada útil para el frontend.
        """
        items = obj.carritoproducto_set.all()
        
        return {
            'items_count': len(items),
            'productos_count': sum(item.cantidad for item in items),
            'subtotal': float(obj.total),
            'descuentos': 0.00,  # Para futuras implementaciones
            'total': float(obj.total)
        }


class AgregarProductoCarritoSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para acciones específicas
    
    Para agregar productos al carrito, validamos disponibilidad y stock.
    """
    
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1, max_value=100)
    
    def validate_producto_id(self, value):
        """Validar que el producto existe y está disponible"""
        try:
            producto = Producto.objects.select_related('stock').get(id=value)
            if not producto.activo:
                raise serializers.ValidationError("El producto no está disponible")
            return value
        except Producto.DoesNotExist:
            raise serializers.ValidationError("El producto no existe")
    
    def validate(self, data):
        """
        📝 MICROCONCEPTO: Validación de stock disponible
        
        Verificamos que hay suficiente stock para la cantidad solicitada.
        """
        try:
            producto = Producto.objects.select_related('stock').get(id=data['producto_id'])
            if producto.stock.stock_actual < data['cantidad']:
                raise serializers.ValidationError({
                    'cantidad': f'Solo hay {producto.stock.stock_actual} unidades disponibles'
                })
        except Producto.DoesNotExist:
            pass  # Ya validado en validate_producto_id
        
        return data


class ActualizarCantidadCarritoSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para actualizar cantidad
    
    Permite modificar la cantidad de un producto ya en el carrito.
    """
    
    cantidad = serializers.IntegerField(min_value=1, max_value=100)
    
    def __init__(self, *args, **kwargs):
        self.carrito_producto = kwargs.pop('carrito_producto', None)
        super().__init__(*args, **kwargs)
    
    def validate_cantidad(self, value):
        """Validar stock disponible para la nueva cantidad"""
        if self.carrito_producto:
            producto = self.carrito_producto.producto
            if producto.stock.stock_actual < value:
                raise serializers.ValidationError(
                    f'Solo hay {producto.stock.stock_actual} unidades disponibles'
                )
        return value


class ProductoEstadoSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer para filtros por estado
    
    Serializer específico para el CU-E13 de filtrado por estado.
    """
    
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    estado = serializers.SerializerMethodField()
    stock_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'precio_venta', 'categoria', 
            'stock_actual', 'estado'
        ]
    
    def get_stock_actual(self, obj):
        """Stock actual del producto"""
        return obj.stock.stock_actual if hasattr(obj, 'stock') else 0
    
    def get_estado(self, obj):
        """
        📝 MICROCONCEPTO: Determinación de estado del producto
        
        Estados:
        - disponible: stock > 0 y producto activo
        - agotado: stock = 0 pero producto activo
        - no_disponible: producto inactivo
        """
        if not obj.activo:
            return 'no_disponible'
        elif not hasattr(obj, 'stock') or obj.stock.stock_actual <= 0:
            return 'agotado'
        else:
            return 'disponible'


class ProductoStatsSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para estadísticas
    
    No hereda de ModelSerializer porque representa datos agregados,
    no un modelo específico.
    """
    
    total_productos = serializers.IntegerField()
    productos_activos = serializers.IntegerField()
    productos_sin_stock = serializers.IntegerField()
    productos_stock_bajo = serializers.IntegerField()
    categorias_count = serializers.IntegerField()
    valor_inventario = serializers.DecimalField(max_digits=12, decimal_places=2)
    productos_mas_vendidos = serializers.ListField(child=serializers.DictField())
    stock_critico = serializers.ListField(child=serializers.DictField())


class ResumenEstadosSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para resumen de estados
    
    Para el endpoint de resumen del CU-E13.
    """
    
    resumen_estados = serializers.DictField()
    total_productos = serializers.IntegerField()
    productos_activos = serializers.IntegerField()
    productos_inactivos = serializers.IntegerField()
