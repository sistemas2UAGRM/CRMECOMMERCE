# apps/crm/calendario/models.py
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class EventoCalendario(models.Model):
    """
    Un evento o cita en el calendario de un empleado.
    Ej: "Reunión de seguimiento con Juan Pérez"
    """
    
    # El "dueño" del evento (a qué calendario de empleado pertenece)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos_calendario'
    )
    
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    # Otros empleados de la boutique invitados al evento
    invitados = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='eventos_invitados',
        blank=True
    )

    # --- Vínculo Genérico (Conexión al CRM) ---
    # A qué (Potencial, Contacto, Oportunidad) se refiere este evento.
    # 
    # Hacemos que sea opcional (un empleado puede agendar "Vacaciones")
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True
    )
    # Usamos PositiveIntegerField porque los IDs de Potencial, etc., son numéricos
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # El campo 'relacionado_con' es el que usaremos en la API
    relacionado_con = GenericForeignKey('content_type', 'object_id')
    # --- Fin del Vínculo ---

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento de Calendario"
        verbose_name_plural = "Eventos de Calendario"
        ordering = ('fecha_inicio',) # Ordenar por fecha de inicio

    def __str__(self):
        return f"{self.titulo} ({self.propietario.email})"