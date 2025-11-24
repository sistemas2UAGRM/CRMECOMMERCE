# /apps/ecommerce/carritos/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.db import transaction

from .models import Carrito, ItemCarrito
from .serializers import CarritoSerializer, ItemCarritoWriteSerializer
from ..pedidos.models import Pedido, DetallePedido
from ..pedidos.serializers import PedidoSerializer
from ..productos.models import ArticuloAlmacen

class CarritoViewSet(viewsets.ViewSet):
    """
    Endpoint para gestionar el carrito del usuario autenticado.
    - GET /api/ecommerce/carrito/: Devuelve el carrito actual.
    - POST /api/ecommerce/carrito/agregar_item/: Agrega o actualiza un producto.
    - DELETE /api/ecommerce/carrito/eliminar_item/{item_id}/: Elimina un item.
    - POST /api/ecommerce/carrito/crear_pedido/: Convierte el carrito en un pedido.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Obtiene o crea el carrito para el usuario.
        carrito, _ = Carrito.objects.get_or_create(usuario=self.request.user)
        return carrito

    def list(self, request):
        """Obtiene el contenido del carrito del usuario."""
        carrito = self.get_object()
        serializer = CarritoSerializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def agregar_item(self, request):
        """Agrega o actualiza la cantidad de un producto en el carrito."""
        carrito = self.get_object()
        serializer = ItemCarritoWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = serializer.validated_data['producto']
        cantidad = serializer.validated_data['cantidad']

        # Verificar stock disponible antes de agregar al carrito
        stock_disponible = producto.stock_total()
        if cantidad > stock_disponible:
            return Response(
                {'error': f'Stock insuficiente para "{producto.nombre}". Disponible: {stock_disponible}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if stock_disponible <= 0:
            return Response(
                {'error': f'El producto "{producto.nombre}" no tiene stock disponible.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Si el item ya existe, actualiza la cantidad. Si no, lo crea.
        item, created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        if not created:
            item.cantidad = cantidad
            item.save()

        carrito_serializer = CarritoSerializer(carrito)
        return Response(carrito_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='eliminar_item')
    def eliminar_item(self, request, pk=None):
        """Elimina un item específico del carrito."""
        carrito = self.get_object()
        try:
            item = ItemCarrito.objects.get(id=pk, carrito=carrito)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ItemCarrito.DoesNotExist:
            return Response({'error': 'Item no encontrado en el carrito.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def crear_pedido(self, request):
        """
        Convierte el carrito actual en un nuevo pedido.
        
        Body esperado:
        {
            "metodo_pago": "tarjeta",  // opcional: 'tarjeta', 'transferencia', 'efectivo', 'paypal'
            "direccion_envio": "Calle Principal 123, Ciudad",  // opcional
            "comentario": "Dejar en portería"  // opcional
        }
        """
        carrito = self.get_object()
        if not carrito.items.exists():
            return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Generar código único para el pedido
        import uuid
        codigo_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"

        # 2. Crear el Pedido con los datos del body
        pedido = Pedido.objects.create(
            codigo=codigo_pedido,
            cliente=request.user,
            metodo_pago=request.data.get('metodo_pago', None),
            direccion_envio=request.data.get('direccion_envio', ''),
            comentario=request.data.get('comentario', None)
        )

        # 3. Mover items del carrito a detalles de pedido y reservar stock
        for item_carrito in carrito.items.all():
            producto = item_carrito.producto
            stock_disponible = producto.stock_total()
            
            if item_carrito.cantidad > stock_disponible:
                raise ValidationError(f"Stock insuficiente para '{producto.nombre}' al crear el pedido.")

            # Crear el detalle del pedido
            detalle = DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item_carrito.cantidad,
                precio_unitario=item_carrito.precio_capturado,
                nombre_producto=producto.nombre
            )
            # Calcular y guardar el subtotal del detalle
            detalle.calcular_subtotal()
            detalle.save()
            
            # Reservar stock (lógica simplificada, asume un solo almacén por ahora)
            # Para múltiples almacenes, se necesitaría una estrategia de selección (ej: FIFO)
            articulo_almacen = ArticuloAlmacen.objects.filter(producto=producto).first()
            if articulo_almacen:
                articulo_almacen.reservado += item_carrito.cantidad
                articulo_almacen.save()

        # 4. Calcular totales del pedido
        pedido.calcular_totales()
        pedido.save()

        # 5. Limpiar el carrito
        carrito.items.all().delete()

        # 6. Devolver el nuevo pedido
        serializer = PedidoSerializer(pedido)
        return Response(serializer.data, status=status.HTTP_201_CREATED)