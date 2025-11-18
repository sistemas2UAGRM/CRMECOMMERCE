# apps/crm/soporte/models.py
from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField
from apps.ecommerce.pedidos.models import Pedido

class Ticket(models.Model):
    """
    Un ticket de soporte o reclamación iniciado por un cliente.
    Ej: "Mi pedido no ha llegado", "Producto defectuoso".
    """
    class EstadoTicket(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        RESUELTO = 'RESUELTO', 'Resuelto'
        CERRADO = 'CERRADO', 'Cerrado'

    class PrioridadTicket(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'

    # El cliente que abrió el ticket
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    
    # El empleado/admin que está asignado a este ticket
    agente_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_asignados',
        # Limitar a solo staff
        limit_choices_to={'is_staff': True}
    )
    
    # Vínculo opcional a un pedido específico
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    
    asunto = models.CharField(max_length=255)
    
    estado = models.CharField(
        max_length=20, 
        choices=EstadoTicket.choices, 
        default=EstadoTicket.ABIERTO
    )
    
    prioridad = models.CharField(
        max_length=20, 
        choices=PrioridadTicket.choices, 
        default=PrioridadTicket.MEDIA
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ticket de Soporte"
        verbose_name_plural = "Tickets de Soporte"
        ordering = ('-actualizado_en',) # Los más recientes primero

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto} ({self.get_estado_display()})"



class MensajeTicket(models.Model):
    """
    Un mensaje individual dentro de un Ticket (la conversación).
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    
    # El usuario que envía el mensaje (puede ser el cliente o un admin)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_ticket'
    )
    
    mensaje = models.TextField()
    
    # Campo opcional para adjuntar una foto (ej. producto roto)
    adjunto = CloudinaryField(
        'soporte/adjuntos',
        blank=True, 
        null=True
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensaje de Ticket"
        verbose_name_plural = "Mensajes de Ticket"
        ordering = ('creado_en',) # El más antiguo primero (orden de chat)

    def __str__(self):
        return f"Mensaje de {self.usuario.email} en Ticket #{self.ticket.id}"