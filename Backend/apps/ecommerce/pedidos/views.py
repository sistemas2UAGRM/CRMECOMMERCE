from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pedido, DetallePedido
from .serializers import PedidoSerializer, DetallePedidoSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
import stripe
from django.conf import settings

# Configurar Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

class EsPropietarioOPermisoAdmin(permissions.BasePermission):
    """
    Permite acceso si el usuario es admin o si es el cliente dueño del pedido.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.cliente == request.user

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().select_related('cliente').prefetch_related('detalles__producto')
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'cliente__username', 'cliente__email', 'estado']
    ordering_fields = ['fecha_creacion', 'total', 'estado']
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        # Permisos: listar y crear cualquier usuario autenticado; retrieve/update/delete solo propietario o admin
        if self.action in ['list', 'create']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), EsPropietarioOPermisoAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        # si no es admin devolver solo pedidos del usuario actual
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            qs = qs.filter(cliente=self.request.user)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def marcar_pagado(self, request, pk=None):
        pedido = self.get_object()
        pedido.pagado = True
        pedido.estado = Pedido.ESTADO_PAGADO
        pedido.save()
        return Response({'status': 'pedido marcado como pagado'})

    @action(detail=True, methods=['post'], url_path='iniciar-pago')
    def iniciar_pago(self, request, pk=None):
        """
        Crea un PaymentIntent de Stripe para el pedido.
        """
        pedido = self.get_object()
        if pedido.pagado:
            return Response({'error': 'Este pedido ya ha sido pagado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que Stripe esté configurado
        if not stripe.api_key or stripe.api_key == '':
            return Response({
                'error': 'Stripe no está configurado correctamente. Por favor, agrega tu STRIPE_SECRET_KEY en el archivo .env'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Stripe maneja montos en la unidad monetaria más pequeña (ej. centavos)
            monto_en_centavos = int(pedido.total * 100)
            
            # Crear PaymentIntent de Stripe
            intent = stripe.PaymentIntent.create(
                amount=monto_en_centavos,
                currency='usd',
                metadata={
                    'pedido_id': pedido.id,
                    'pedido_codigo': pedido.codigo,
                    'cliente_username': pedido.cliente.username if pedido.cliente else 'Anónimo',
                    'cliente_email': pedido.cliente.email if pedido.cliente else '',
                },
                description=f'Pedido {pedido.codigo}',
            )
            
            # Opcional: Crear un registro de pago preliminar si tienes el modelo Pago
            # from ..pagos.models import Pago
            # Pago.objects.create(
            #     pedido=pedido,
            #     id_transaccion_proveedor=intent.id,
            #     monto=pedido.total,
            #     moneda='USD'
            # )
            
            return Response({
                'clientSecret': intent.client_secret,
                'pedido_id': pedido.id,
                'pedido_codigo': pedido.codigo,
                'total': float(pedido.total),
            })
            
        except Exception as e:
            # Capturar cualquier error (incluidos los de Stripe)
            error_message = str(e)
            print(f"Error en iniciar_pago: {error_message}")  # Para debugging
            return Response({'error': f'Error al procesar el pago: {error_message}'}, status=status.HTTP_400_BAD_REQUEST)

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all().select_related('producto', 'pedido')
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # por defecto solo admin puede manipular detalles directos
