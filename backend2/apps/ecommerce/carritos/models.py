# /apps/ecommerce/carritos/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# Importamos el modelo Producto de tu app de productos
from ..productos.models import Producto

class Carrito(models.Model):
    """
    Un único carrito de compras por usuario.
    """
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    @property
    def subtotal(self):
        """Calcula el subtotal sumando los subtotales de todos los items."""
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        """Calcula la cantidad total de productos en el carrito."""
        return sum(item.cantidad for item in self.items.all())

class ItemCarrito(models.Model):
    """
    Representa un producto dentro del carrito, con su cantidad.
    """
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='items_carrito')
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    
    # Guarda el precio al momento de añadirlo para evitar inconsistencias si el precio del producto cambia.
    precio_capturado = models.DecimalField(max_digits=12, decimal_places=2, help_text="Precio al momento de añadir al carrito")
    
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Evita tener el mismo producto dos veces en el mismo carrito.
        unique_together = ('carrito', 'producto')
        ordering = ['-agregado_en']

    @property
    def subtotal(self):
        return self.precio_capturado * self.cantidad

    def save(self, *args, **kwargs):
        # Captura el precio del producto automáticamente si es un item nuevo.
        if self._state.adding:
            self.precio_capturado = self.producto.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en {self.carrito}"