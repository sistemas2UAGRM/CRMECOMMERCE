from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pedido, DetallePedido
from .serializers import PedidoSerializer, DetallePedidoSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

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

class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all().select_related('producto', 'pedido')
    serializer_class = DetallePedidoSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # por defecto solo admin puede manipular detalles directos
