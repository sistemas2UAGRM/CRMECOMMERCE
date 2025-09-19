# core/ecommerce/models.py
from django.db import models
from django.conf import settings  # para referenciar nuestro User Personalizado
from django.utils import timezone

class Categoria(models.Model):
   nombre = models.CharField(max_length=255, unique=True)
   descripcion = models.TextField(blank=True, null=True)
   fecha_creacion = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.nombre
   
class Stock(models.Model):
   stock_min = models.PositiveIntegerField(default=0)
   stock_actual = models.PositiveIntegerField(default=0)

   def __str__(self):
      return f"Actual: {self.stock_actual} (Min: {self.stock_min})"

class Producto(models.Model):
   nombre = models.CharField(max_length=255)
   descripcion = models.TextField(blank=True, null=True)
   precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
   garantia = models.CharField(max_length=255, blank=True, null=True)
   activo = models.BooleanField(default=True)
   fecha_creacion = models.DateTimeField(auto_now_add=True)
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
   usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
   estado = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='ABIERTO')
   total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
   productos = models.ManyToManyField(Producto, through='CarritoProducto')
   fecha_creacion = models.DateTimeField(auto_now_add=True)
   fecha_actualizacion = models.DateTimeField(auto_now=True)

   def calcular_total(self):
      """Calcula el total del carrito basado en los productos"""
      total = sum(
         item.producto.precio_venta * item.cantidad 
         for item in self.carritoproducto_set.all()
      )
      self.total = total
      self.save()
      return total

   def __str__(self):
      return f"Carrito de {self.usuario.username} - {self.estado}"

class CarritoProducto(models.Model):
   carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
   producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
   cantidad = models.PositiveIntegerField(default=1)
   fecha_agregado = models.DateTimeField(auto_now_add=True)

   class Meta:
      # Asegura que no se pueda anadir el mismo producto dos veces al mismo Carrito
      unique_together = ('carrito', 'producto')

   def __str__(self):
      return f"{self.producto.nombre} x{self.cantidad} en carrito de {self.carrito.usuario.username}"

