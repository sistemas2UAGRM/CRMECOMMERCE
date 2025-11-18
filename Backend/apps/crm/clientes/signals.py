# apps/crm/clientes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cliente

from apps.ecommerce.pedidos.models import Pedido
from apps.users.models import User 

@receiver(post_save, sender=User)
def crear_perfil_cliente(sender, instance, created, **kwargs):
    """
    Crea un perfil de Cliente automáticamente cuando se
    crea un nuevo CustomUser.
    """
    if created:
        Cliente.objects.create(usuario=instance)

@receiver(post_save, sender=Pedido)
def actualizar_perfil_cliente(sender, instance, **kwargs):
    """
    Escucha cambios en el modelo Pedido.
    Si un pedido se marca como PAGADO, recalcula las
    estadísticas del perfil del cliente.
    """
    pedido = instance
    
    # Verificamos si el pedido se acaba de marcar como pagado
    # (o el estado que uses para "completado")
    if pedido.estado == Pedido.EstadoPedido.PAGADO and pedido.usuario:
        # Usamos 'get' porque el signal 'crear_perfil_cliente'
        # asegura que el perfil siempre exista.
        cliente_perfil = Cliente.objects.get(usuario=pedido.usuario)
        
        # Llamamos al método que definimos en el modelo
        cliente_perfil.recalcular_estadisticas()