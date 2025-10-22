# /apps/ecommerce/carritos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Carrito

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_carrito_para_nuevo_usuario(sender, instance, created, **kwargs):
    """
    Crea un objeto Carrito cada vez que se crea un nuevo User.
    """
    if created:
        Carrito.objects.create(usuario=instance)