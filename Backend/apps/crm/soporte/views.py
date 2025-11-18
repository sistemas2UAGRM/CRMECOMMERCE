# apps/crm/soporte/views.py
from rest_framework import viewsets, generics, permissions, mixins, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Ticket, MensajeTicket
from .serializers import (
    TicketSerializer, 
    TicketCreateSerializer, 
    TicketUpdateSerializer, 
    MensajeCreateSerializer
)

# --- 1. Vistas para el CLIENTE ---
class ClienteTicketViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    """
    (CLIENTE) ViewSet para que un cliente vea su historial
    de tickets y cree nuevos.
    
    Endpoints:
    GET /api/soporte/tickets/ (Listar mis tickets)
    POST /api/soporte/tickets/ (Crear un ticket)
    GET /api/soporte/tickets/{id}/ (Ver un ticket mío)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Sobrescribe para devolver SÓLO los tickets del usuario logueado."""
        return Ticket.objects.filter(
            cliente=self.request.user
        ).prefetch_related('mensajes')

    def get_serializer_class(self):
        """Usa un serializador para crear y otro para leer."""
        if self.action == 'create':
            return TicketCreateSerializer
        return TicketSerializer # Para 'list' y 'retrieve'

    def get_serializer_context(self):
        """Pasa el request al TicketCreateSerializer."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

# --- 2. Vistas para el ADMINISTRADOR ---
class AdminTicketViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    (ADMIN) ViewSet para que un admin gestione TODOS los tickets.
    
    Endpoints:
    GET /api/soporte/admin/tickets/ (Listar TODOS los tickets)
    GET /api/soporte/admin/tickets/{id}/ (Ver CUALQUIER ticket)
    PATCH /api/soporte/admin/tickets/{id}/ (Actualizar estado/agente)
    """
    permission_classes = [permissions.IsAdminUser] # Solo staff/admin
    queryset = Ticket.objects.all().select_related(
        'cliente', 'agente_asignado'
    ).prefetch_related('mensajes')
    
    filterset_fields = ['estado', 'prioridad', 'agente_asignado', 'cliente']
    search_fields = ['asunto', 'cliente__email', 'pedido__id']

    def get_serializer_class(self):
        """Usa un serializador para actualizar y otro para leer."""
        if self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        return TicketSerializer # Para 'list' y 'retrieve'

# --- 3. Vista de ACCIÓN (para Cliente y Admin) ---
class MensajeCreateView(generics.CreateAPIView):
    """
    Vista para que un CLIENTE o ADMIN añada un mensaje
    (responda) a un ticket existente.
    
    Endpoint:
    POST /api/soporte/tickets/{ticket_pk}/responder/
    """
    serializer_class = MensajeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Pasa el 'request' y el 'ticket' al serializador.
        """
        # 1. Obtener el ticket_pk de la URL
        ticket_pk = self.kwargs['ticket_pk']
        # 2. Obtener el objeto Ticket
        ticket = get_object_or_404(Ticket, id=ticket_pk)
        
        # 3. ¡Control de Seguridad!
        # El usuario debe ser el dueño del ticket O un admin
        if not (self.request.user.is_staff or ticket.cliente == self.request.user):
            raise PermissionDenied("No tienes permiso para responder a este ticket.")

        # 4. Pasar el contexto al serializador
        context = super().get_serializer_context()
        context['request'] = self.request
        context['ticket'] = ticket
        return context
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe 'create' para que al responder, el estado del
        ticket se vuelva a poner "En Proceso" (si lo cerró un cliente).
        """
        # (Llama a get_serializer_context() implícitamente)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # El serializer's .create() guarda el mensaje
        mensaje = serializer.save() 
        
        ticket = mensaje.ticket
        
        # Lógica de negocio: si el cliente responde,
        # el ticket se reabre si el admin lo había resuelto.
        if not request.user.is_staff and ticket.estado == Ticket.EstadoTicket.RESUELTO:
            ticket.estado = Ticket.EstadoTicket.EN_PROCESO
            ticket.save()

        # Devolvemos el ticket completo y actualizado
        read_serializer = TicketSerializer(ticket)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)