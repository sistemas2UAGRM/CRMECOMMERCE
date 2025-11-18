# apps/crm/clientes/models.py
from django.db import models
from django.db.models import Sum, Count
from django.conf import settings 

from apps.ecommerce.pedidos.models import Pedido 

class Segmento(models.Model):
    """
    Un segmento de clientes.
    Ej: "Clientes VIP", "Clientes Nuevos", "Clientes en Riesgo"
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Segmento"
        verbose_name_plural = "Segmentos"
    
    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    """
    El "Perfil 360" de un cliente. Se conecta 1-a-1 con el modelo de Usuario.
    """
    class EstadoCliente(models.TextChoices):
        NUEVO = 'NUEVO', 'Nuevo' # Recién registrado
        ACTIVO = 'ACTIVO', 'Activo' # Ha comprado recientemente
        VIP = 'VIP', 'VIP' # Ha gastado mucho
        RIESGO = 'RIESGO', 'En Riesgo' # No ha comprado en mucho tiempo

    # --- Vínculos ---
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_cliente'
    )
    
    # A qué segmentos pertenece este cliente
    segmentos = models.ManyToManyField(
        Segmento,
        blank=True,
        related_name='clientes'
    )
    
    estado = models.CharField(
        max_length=20, 
        choices=EstadoCliente.choices, 
        default=EstadoCliente.NUEVO
    )

    # --- Campos Agregados (La magia del CRM) ---
    # Estos campos se actualizarán automáticamente con 'signals'
    total_gastado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    total_pedidos = models.PositiveIntegerField(default=0)
    
    fecha_ultima_compra = models.DateTimeField(
        null=True, 
        blank=True
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente (Perfil 360)"
        verbose_name_plural = "Clientes (Perfiles 360)"

    def __str__(self):
        return self.usuario.email
    
    def recalcular_estadisticas(self):
        """
        Calcula y actualiza las estadísticas de compra de este cliente.
        """
        pedidos_pagados = Pedido.objects.filter(
            usuario=self.usuario,
            estado=Pedido.EstadoPedido.PAGADO # O el estado que uses para 'completado'
        )
        
        # 1. Calcular agregados
        agregados = pedidos_pagados.aggregate(
            total=Sum('total_pedido'),
            conteo=Count('id')
        )
        
        # 2. Obtener última compra
        ultimo_pedido = pedidos_pagados.order_by('-creado_en').first()
        
        # 3. Actualizar el objeto
        self.total_gastado = agregados['total'] or 0
        self.total_pedidos = agregados['conteo'] or 0
        self.fecha_ultima_compra = ultimo_pedido.creado_en if ultimo_pedido else None
        
        # 4. (Lógica de Segmentación simple)
        if self.total_gastado > 1000: # Ej: Más de 1000 Bs es VIP
            self.estado = self.EstadoCliente.VIP
        elif self.total_pedidos > 0:
            self.estado = self.EstadoCliente.ACTIVO
        
        self.save()