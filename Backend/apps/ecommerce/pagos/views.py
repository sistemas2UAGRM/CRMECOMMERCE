# /apps/ecommerce/pagos/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction

from .models import Pago
from .serializers import PagoSerializer
from ..pedidos.models import Pedido
from ..productos.models import ArticuloAlmacen, StockMovimiento

import stripe

# Configura tu clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class PagoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura para que los administradores vean los pagos.
    """
    queryset = Pago.objects.all().order_by('-creado_en')
    serializer_class = PagoSerializer
    permission_classes = [permissions.IsAdminUser]


class StripeWebhookView(APIView):
    """
    Escucha los webhooks de Stripe para actualizar el estado de los pagos y pedidos.
    """
    permission_classes = [permissions.AllowAny] # Stripe no se autenticará

    @transaction.atomic
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Payload inválido
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Firma inválida
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Manejar el evento `payment_intent.succeeded`
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            pedido_id = payment_intent['metadata'].get('pedido_id')
            
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                
                # 1. Actualizar o crear el registro de Pago
                Pago.objects.update_or_create(
                    id_transaccion_proveedor=payment_intent['id'],
                    defaults={
                        'pedido': pedido,
                        'monto': payment_intent['amount'] / 100.0, # Stripe usa centavos
                        'moneda': payment_intent['currency'].upper(),
                        'estado': Pago.ESTADO_EXITOSO,
                        'datos_respuesta': payment_intent,
                    }
                )
                
                # 2. Actualizar el Pedido
                pedido.pagado = True
                pedido.estado = Pedido.ESTADO_PAGADO
                pedido.save()

                # 3. Mover stock: de reservado a salida definitiva
                for detalle in pedido.detalles.all():
                    articulo_almacen = ArticuloAlmacen.objects.filter(producto=detalle.producto).first()
                    if articulo_almacen:
                        # Reducir cantidad y reserva
                        articulo_almacen.cantidad -= detalle.cantidad
                        articulo_almacen.reservado -= detalle.cantidad
                        articulo_almacen.save()
                    
                    # Crear movimiento de stock para auditoría
                    StockMovimiento.objects.create(
                        producto=detalle.producto,
                        almacen=articulo_almacen.almacen if articulo_almacen else None,
                        cantidad=detalle.cantidad, # Cantidad es positiva, tipo es 'salida'
                        tipo='salida',
                        referencia=f"Venta Pedido {pedido.codigo}",
                        usuario=pedido.cliente
                    )

            except Pedido.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

        # Puedes añadir más manejadores de eventos como 'payment_intent.payment_failed'
        
        return Response(status=status.HTTP_200_OK)