# apps/crm/calendario/views.py
from rest_framework import viewsets, permissions
from .models import EventoCalendario
from .serializers import EventoCalendarioSerializer

class EventoCalendarioViewSet(viewsets.ModelViewSet):
    """
    (STAFF) CRUD completo para Eventos de Calendario.
    Un empleado solo puede ver y gestionar SUS PROPIOS eventos.
    Un superadmin puede ver todos.
    """
    serializer_class = EventoCalendarioSerializer
    permission_classes = [permissions.IsAdminUser] # Solo staff/admin pueden ver el calendario

    def get_queryset(self):
        """
        Filtra los eventos para que un empleado vea solo los suyos.
        Un superadmin puede ver todos los eventos.
        """
        user = self.request.user
        
        # Si es superadmin, mostramos todos los calendarios
        if user.is_superuser:
            return EventoCalendario.objects.all()
        
        # Si es un empleado normal, muestra solo sus eventos
        # (donde es propietario O donde está invitado)
        return EventoCalendario.objects.filter(
            models.Q(propietario=user) | models.Q(invitados=user)
        ).distinct() # .distinct() para evitar duplicados si es propietario Y invitado

    def get_serializer_context(self):
        """
        Pasa el 'request' al serializador para que sepa
        quién es el 'propietario' (empleado) que crea el evento.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context