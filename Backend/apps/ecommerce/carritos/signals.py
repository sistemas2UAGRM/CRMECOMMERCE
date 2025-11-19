# /apps/ecommerce/carritos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db import connection
from .models import Carrito

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_carrito_para_nuevo_usuario(sender, instance, created, **kwargs):
    """
    Crea un carrito automáticamente para el usuario,
    PERO SOLO si no estamos en el esquema público.
    """
    if created:
        if connection.schema_name == 'public':
            return
        Carrito.objects.create(usuario=instance)