#/apps/crm/crm_preventa/models.py
from django.db import models
from django.conf import settings # Para nuestro CustomUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from ...ecommerce.pedidos.models import Pedido 

# --- 1. El inicio del embudo: POTENCIAL (Lead) ---
class Potencial(models.Model):
    """
    Un Potencial (Lead). Es una persona que podría estar interesada.
    Ej: "Juan Pérez de Instagram".
    """
    class EstadoPotencial(models.TextChoices):
        NUEVO = 'NUEVO', 'Nuevo'
        CONTACTADO = 'CONTACTADO', 'Contactado'
        CALIFICADO = 'CALIFICADO', 'Calificado (Se convirtió en Contacto)'
        NO_CALIFICADO = 'NO_CALIFICADO', 'No Calificado'

    class FuentePotencial(models.TextChoices):
        INSTAGRAM = 'INSTAGRAM', 'Instagram'
        FACEBOOK = 'FACEBOOK', 'Facebook'
        REFERIDO = 'REFERIDO', 'Referido'
        TIENDA_FISICA = 'TIENDA_FISICA', 'Tienda Física'
        OTRO = 'OTRO', 'Otro'

    nombre_completo = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True)
    empresa = models.CharField(max_length=255, blank=True)
    
    fuente = models.CharField(
        max_length=20, 
        choices=FuentePotencial.choices, 
        default=FuentePotencial.OTRO
    )
    estado = models.CharField(
        max_length=20, 
        choices=EstadoPotencial.choices, 
        default=EstadoPotencial.NUEVO
    )
    
    # El "dueño" del potencial (el empleado de tu boutique que lo gestiona)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='potenciales_propios'
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.get_estado_display()})"


# --- 2. El Potencial Calificado: CONTACTO ---
class Contacto(models.Model):
    """
    Un Contacto. Es un Potencial que ha sido calificado.
    Este es el perfil "maestro" del CRM.
    """
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    empresa = models.CharField(max_length=255, blank=True)

    # De dónde vino este contacto (opcional)
    potencial_origen = models.OneToOneField(
        Potencial, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # --- ¡EL PUENTE CLAVE! ---
    # Si este contacto se registra en el E-COMMERCE,
    # lo vinculamos aquí.
    usuario_ecommerce = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacto_crm'
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# --- 3. La Venta en curso: OPORTUNIDAD ---
class Oportunidad(models.Model):
    """
    Una Oportunidad de venta.
    Ej: "Venta de 50 camisas para la empresa X".
    """
    class EtapaOportunidad(models.TextChoices):
        CALIFICACION = 'CALIFICACION', 'Calificación'
        PROPUESTA = 'PROPUESTA', 'Propuesta Presentada'
        NEGOCIACION = 'NEGOCIACION', 'En Negociación'
        GANADA = 'GANADA', 'Cerrada (Ganada)'
        PERDIDA = 'PERDIDA', 'Cerrada (Perdida)'

    nombre = models.CharField(max_length=255, help_text="Ej: Venta de uniformes Empresa X")
    monto_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_cierre_estimada = models.DateField(null=True, blank=True)
    
    etapa = models.CharField(
        max_length=20, 
        choices=EtapaOportunidad.choices, 
        default=EtapaOportunidad.CALIFICACION
    )
    
    # Con quién estamos tratando esta oportunidad
    contacto = models.ForeignKey(
        Contacto, 
        on_delete=models.PROTECT, 
        related_name='oportunidades'
    )
    
    # Quién está a cargo de esta venta
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        related_name='oportunidades_propias'
    )
    
    # --- ¡EL OTRO PUENTE CLAVE! ---
    # Si esta oportunidad se GANA y se convierte en un Pedido
    # del e-commerce, lo vinculamos aquí.
    pedido_ecommerce = models.OneToOneField(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oportunidad_crm'
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_etapa_display()})"


# --- 4. El Seguimiento: ACTIVIDAD ---
class Actividad(models.Model):
    """
    Un registro de seguimiento (llamada, correo, reunión).
    Se usa un GenericForeignKey para vincularse a un
    Potencial, Contacto u Oportunidad.
    """
    class TipoActividad(models.TextChoices):
        LLAMADA = 'LLAMADA', 'Llamada'
        CORREO = 'CORREO', 'Correo Electrónico'
        WHATSAPP = 'WHATSAPP', 'Mensaje (WhatsApp)'
        REUNION = 'REUNION', 'Reunión'
        OTRO = 'OTRO', 'Otro'

    # Quién hizo la actividad (un empleado)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    
    tipo = models.CharField(max_length=20, choices=TipoActividad.choices)
    notas = models.TextField()
    fecha_actividad = models.DateTimeField(auto_now_add=True)

    # --- El Vínculo Genérico (Magia de Django) ---
    # Esto nos permite vincular esta actividad a CUALQUIER otro modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField() # Asumimos que los IDs son UUID, o usa PositiveIntegerField si son numéricos
    content_object = GenericForeignKey('content_type', 'object_id')
    # --- Fin del Vínculo Genérico ---

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ('-fecha_actividad',)

    def __str__(self):
        return f"{self.get_tipo_display()} por {self.propietario} en {self.fecha_actividad.date()}"