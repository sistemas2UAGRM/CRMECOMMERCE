# core/ecommmerce/models.py
from email.policy import default
from enum import unique
from itertools import product
from random import choices
from django.db import models
from django.conf import settings # para referenciar nuestro User Personalizado

class Categoria(models.Model):
   nombre = models.CharField(max_length=255, unique=True)
   descripcion = models.TextField(blank=True, null=True)

   def __str__(self):
      return self.nombre
   
class Stock(models.Model):
   stock_min = models.PositiveIntegerField(default=0)
   stock_actual = models.PositiveIntegerField(default=0)

   def __str__(self):
      return f"Actual: {self.stock_actual} (Min: {self,stock_min})"

class Producto(models.Model):
   nombre = models.CharField(max_length=255)
   descripcion = models.TextField(blank=True, null=True)
   precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
   garantia = models.CharField(max_length=255, blank=True, null=True)
   # Relaciones
   categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
   stock = models.OneToOneField(Stock, on_delete=models.CASCADE, related_name='producto')

   def __str__(self):
      return self.nombre

class Carrito(models.Model):
   ESTADO_OPCIONES = (
      ('ABIERTO', 'Abierto'),
      ('CERRADO', 'Cerrado'),
      ('ABANDONADO', 'Abandonado'),
   )
   usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   estado = models.CharField(max_length=20,choices=ESTADO_OPCIONES, default='ABIERTO')
   total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
   productos = models.ManyToManyField(Producto, through='CarritoProducto')

   def __str__(self):
      return f"Carrito de {self.usuario.username}"

class CarritoProducto(models.Model):
   carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
   producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
   cantidad = models.PositiveIntegerField(default=1)

   class Meta:
      # Asegura que no se pueda anadir el mismo producto dos veces al mismo Carrito
      unique_together = ('carrito', 'producto')

