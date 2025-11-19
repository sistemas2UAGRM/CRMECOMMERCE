# /apps/ecommerce/pagos/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
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


class CrearPaymentIntentView(APIView):
    """
    Crea un PaymentIntent de Stripe para un pedido específico.
    
    POST /api/ecommerce/pagos/crear-payment-intent/
    Body:
    {
        "pedido_id": 3
    }
    
    Respuesta:
    {
        "client_secret": "pi_xxx_secret_yyy",
        "pedido_id": 3,
        "monto": 150.00,
        "moneda": "usd"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        pedido_id = request.data.get('pedido_id')
        
        if not pedido_id:
            return Response(
                {'error': 'pedido_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pedido = Pedido.objects.get(id=pedido_id, cliente=request.user)
        except Pedido.DoesNotExist:
            return Response(
                {'error': 'Pedido no encontrado o no pertenece al usuario'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el pedido no esté ya pagado
        if pedido.pagado or pedido.estado == 'pagado':
            return Response(
                {'error': 'El pedido ya está pagado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Crear PaymentIntent en Stripe
            # El monto debe estar en centavos (multiplicar por 100)
            monto_centavos = int(float(pedido.total) * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='usd',  # Puedes hacerlo configurable
                metadata={
                    'pedido_id': pedido.id,
                    'pedido_codigo': pedido.codigo,
                    'usuario_email': request.user.email
                },
                description=f'Pago para pedido {pedido.codigo}'
            )
            
            # Opcional: Crear registro de pago en estado pendiente
            Pago.objects.create(
                pedido=pedido,
                proveedor='stripe',
                id_transaccion_proveedor=payment_intent.id,
                monto=pedido.total,
                moneda='USD',
                estado=Pago.ESTADO_PENDIENTE,
                datos_respuesta={'payment_intent_created': payment_intent}
            )
            
            return Response({
                'client_secret': payment_intent.client_secret,
                'pedido_id': pedido.id,
                'pedido_codigo': pedido.codigo,
                'monto': float(pedido.total),
                'moneda': 'usd',
                'payment_intent_id': payment_intent.id
            }, status=status.HTTP_200_OK)
            
        except stripe.AuthenticationError as e:
            return Response(
                {'error': f'Error de autenticación con Stripe. Verifica tu API Key: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.StripeError as e:
            return Response(
                {'error': f'Error de Stripe: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerificarEstadoPagoView(APIView):
    """
    Verifica el estado de un PaymentIntent y actualiza el pedido si el pago fue exitoso.
    Este endpoint debe ser llamado por el cliente después de confirmar el pago.
    
    Según la documentación de Stripe, esta es la forma recomendada para mobile apps:
    https://docs.stripe.com/payments/payment-intents/verifying-status
    
    POST /api/ecommerce/pagos/verificar-estado-pago/
    Body:
    {
        "payment_intent_id": "pi_xxx"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return Response(
                {'error': 'payment_intent_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Recuperar el PaymentIntent desde Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Obtener el pedido_id desde los metadata
            pedido_id = payment_intent.metadata.get('pedido_id')
            
            if not pedido_id:
                return Response(
                    {'error': 'No se encontró pedido_id en los metadata del PaymentIntent'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                pedido = Pedido.objects.get(id=pedido_id, cliente=request.user)
            except Pedido.DoesNotExist:
                return Response(
                    {'error': 'Pedido no encontrado o no pertenece al usuario'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verificar el estado del PaymentIntent
            if payment_intent.status == 'succeeded':
                # Solo actualizar si el pedido no está ya marcado como pagado
                if not pedido.pagado:
                    # 1. Actualizar o crear el registro de Pago
                    pago, created = Pago.objects.update_or_create(
                        id_transaccion_proveedor=payment_intent.id,
                        defaults={
                            'pedido': pedido,
                            'monto': payment_intent.amount / 100.0,  # Stripe usa centavos
                            'moneda': payment_intent.currency.upper(),
                            'estado': Pago.ESTADO_EXITOSO,
                            'datos_respuesta': dict(payment_intent),
                        }
                    )
                    
                    # 2. Actualizar el Pedido
                    pedido.pagado = True
                    pedido.estado = 'pagado'
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
                            cantidad=detalle.cantidad,
                            tipo='salida',
                            referencia=f"Venta Pedido {pedido.codigo}",
                            usuario=pedido.cliente
                        )
                
                return Response({
                    'status': 'succeeded',
                    'pedido_id': pedido.id,
                    'pedido_codigo': pedido.codigo,
                    'pedido_estado': pedido.estado,
                    'pagado': pedido.pagado,
                    'mensaje': 'Pago confirmado exitosamente'
                }, status=status.HTTP_200_OK)
                
            elif payment_intent.status == 'processing':
                return Response({
                    'status': 'processing',
                    'pedido_id': pedido.id,
                    'mensaje': 'El pago está en proceso'
                }, status=status.HTTP_200_OK)
                
            elif payment_intent.status == 'requires_payment_method':
                return Response({
                    'status': 'requires_payment_method',
                    'pedido_id': pedido.id,
                    'mensaje': 'Se requiere un método de pago válido'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({
                    'status': payment_intent.status,
                    'pedido_id': pedido.id,
                    'mensaje': f'Estado del pago: {payment_intent.status}'
                }, status=status.HTTP_200_OK)
            
        except stripe.StripeError as e:
            return Response(
                {'error': f'Error de Stripe: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error inesperado: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StripeWebhookView(APIView):
    """
    Escucha los webhooks de Stripe para actualizar el estado de los pagos y pedidos.
    
    Para desarrollo local, usa Stripe CLI:
    stripe listen --forward-to 20.171.166.152:8000/api/ecommerce/pagos/webhooks/stripe/
    
    Para producción, configura el webhook en: https://dashboard.stripe.com/webhooks
    """
    permission_classes = [permissions.AllowAny]  # Stripe no se autenticará

    @transaction.atomic
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        # Si no hay secret configurado, retornar error
        if not endpoint_secret:
            return Response(
                {'error': 'STRIPE_WEBHOOK_SECRET no configurado'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Payload inválido
            return Response({'error': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Firma inválida
            return Response({'error': 'Firma inválida'}, status=status.HTTP_400_BAD_REQUEST)

        # Manejar el evento `payment_intent.succeeded`
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            pedido_id = payment_intent['metadata'].get('pedido_id')
            
            if not pedido_id:
                return Response({'error': 'No se encontró pedido_id en metadata'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                pedido = Pedido.objects.get(id=pedido_id)
                
                # Solo actualizar si el pedido no está ya marcado como pagado
                if not pedido.pagado:
                    # 1. Actualizar o crear el registro de Pago
                    Pago.objects.update_or_create(
                        id_transaccion_proveedor=payment_intent['id'],
                        defaults={
                            'pedido': pedido,
                            'monto': payment_intent['amount'] / 100.0,  # Stripe usa centavos
                            'moneda': payment_intent['currency'].upper(),
                            'estado': Pago.ESTADO_EXITOSO,
                            'datos_respuesta': payment_intent,
                        }
                    )
                    
                    # 2. Actualizar el Pedido
                    pedido.pagado = True
                    pedido.estado = 'pagado'
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
                            cantidad=detalle.cantidad,
                            tipo='salida',
                            referencia=f"Venta Pedido {pedido.codigo}",
                            usuario=pedido.cliente
                        )

            except Pedido.DoesNotExist:
                return Response({'error': 'Pedido no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            pedido_id = payment_intent['metadata'].get('pedido_id')
            
            if pedido_id:
                try:
                    Pago.objects.update_or_create(
                        id_transaccion_proveedor=payment_intent['id'],
                        defaults={
                            'estado': Pago.ESTADO_FALLIDO,
                            'datos_respuesta': payment_intent,
                        }
                    )
                except Exception:
                    pass  # No es crítico si falla
        
        return Response(status=status.HTTP_200_OK)