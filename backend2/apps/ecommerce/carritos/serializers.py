# /apps/ecommerce/carritos/serializers.py
from rest_framework import serializers
from .models import Carrito, ItemCarrito
from ..productos.models import Producto
from ..productos.serializers import ProductoListSerializer

class ItemCarritoWriteSerializer(serializers.ModelSerializer):
    """Serializer para añadir/actualizar items. Solo necesita el ID y la cantidad."""
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.filter(activo=True),
        source='producto'
    )

    class Meta:
        model = ItemCarrito
        fields = ['producto_id', 'cantidad']

    def validate(self, data):
        producto = data['producto']
        cantidad = data['cantidad']
        stock_disponible = producto.stock_total()

        if cantidad > stock_disponible:
            raise serializers.ValidationError(
                f"Stock insuficiente para '{producto.nombre}'. Disponible: {stock_disponible}, solicitado: {cantidad}."
            )
        return data

class ItemCarritoReadSerializer(serializers.ModelSerializer):
    """Serializer para leer items, con la información completa del producto."""
    producto = ProductoListSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarrito
        fields = ['id', 'producto', 'cantidad', 'precio_capturado', 'subtotal']


class CarritoSerializer(serializers.ModelSerializer):
    """Serializer principal para el carrito, con items anidados y totales."""
    items = ItemCarritoReadSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Carrito
        fields = ['id', 'usuario', 'subtotal', 'total_items', 'actualizado_en', 'items']