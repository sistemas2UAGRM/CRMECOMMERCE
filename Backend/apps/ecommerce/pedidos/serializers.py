# backend/apps/ecommerce/pedidos/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Pedido, DetallePedido
from ..productos.models import Producto
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_id = serializers.PrimaryKeyRelatedField(source='producto', queryset=Producto.objects.all())
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto_id', 'nombre_producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal']
        read_only_fields = ['subtotal', 'nombre_producto']

    def validate(self, data):
        producto = data.get('producto')
        cantidad = data.get('cantidad', 1)
        if hasattr(producto, 'stock'):
            # si tu modelo producto tiene campo stock
            if producto.stock is not None and producto.stock < cantidad:
                raise serializers.ValidationError(f"Stock insuficiente para {producto}. Disponible: {producto.stock}")
        return data

    def create(self, validated_data):
        # nombre_producto y subtotal se rellenan automáticamente
        producto = validated_data['producto']
        validated_data['nombre_producto'] = producto.nombre if hasattr(producto, 'nombre') else str(producto)
        detalle = DetallePedido(**validated_data)
        detalle.calcular_subtotal()
        detalle.save()
        return detalle


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)
    cliente_id = serializers.PrimaryKeyRelatedField(source='cliente',
                    queryset=User.objects.all(),
                    required=False,
                    allow_null=True
    )

    class Meta:
        model = Pedido
        fields = ['id', 'codigo', 'cliente_id', 'fecha_creacion', 'estado', 'metodo_pago',
                  'direccion_envio', 'subtotal', 'impuestos', 'total', 'comentario', 'detalles',
                  'enviado', 'pagado']
        read_only_fields = ['fecha_creacion', 'subtotal', 'impuestos', 'total']

    def generar_codigo(self):
        # Generador simple de código; puedes reemplazar con tu lógica
        import uuid
        return f"PED-{uuid.uuid4().hex[:8].upper()}"

    @transaction.atomic
    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles', [])
        # Si no viene codigo, generar
        if not validated_data.get('codigo'):
            validated_data['codigo'] = self.generar_codigo()
        pedido = Pedido.objects.create(**validated_data)
        # crear detalles
        for det in detalles_data:
            det['pedido'] = pedido
            # rellenar precio_unitario desde Producto si no viene
            producto = det.get('producto')
            if producto and (not det.get('precio_unitario') or float(det.get('precio_unitario')) == 0.0):
                det['precio_unitario'] = getattr(producto, 'precio', getattr(producto, 'precio_unitario', 0.0))
            detalle_serializer = DetallePedidoSerializer(data=det)
            detalle_serializer.is_valid(raise_exception=True)
            detalle_serializer.save()
            # opcional: reducir stock
            if hasattr(producto, 'stock'):
                # intenta actualizar stock si existe
                producto.stock = producto.stock - detalle_serializer.instance.cantidad
                producto.save()
        # recalcular totales (ej: 18% de impuestos -> ajuste si necesitas otro valor)
        impuesto_rate = getattr(settings, 'PEDIDO_IMPUESTO_RATE', 0.0)
        pedido.calcular_totales(impuesto_rate=impuesto_rate)
        pedido.save()
        return pedido

    @transaction.atomic
    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles', None)
        # actualizar campos simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detalles_data is not None:
            # eliminar detalles existentes y volver a crear (alternativa: lógica de patch)
            instance.detalles.all().delete()
            for det in detalles_data:
                det['pedido'] = instance
                producto = det.get('producto')
                if producto and (not det.get('precio_unitario') or float(det.get('precio_unitario')) == 0.0):
                    det['precio_unitario'] = getattr(producto, 'precio', getattr(producto, 'precio_unitario', 0.0))
                detalle_serializer = DetallePedidoSerializer(data=det)
                detalle_serializer.is_valid(raise_exception=True)
                detalle_serializer.save()
        impuesto_rate = getattr(settings, 'PEDIDO_IMPUESTO_RATE', 0.0)
        instance.calcular_totales(impuesto_rate=impuesto_rate)
        instance.save()
        return instance
