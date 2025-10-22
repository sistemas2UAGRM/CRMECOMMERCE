from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError

class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Categorías"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Almacen(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Producto(models.Model):
    codigo = models.CharField(max_length=64, unique=True, help_text="Código SKU o referencia")
    nombre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))])
    moneda = models.CharField(max_length=10, default="USD")
    peso = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensiones = models.CharField(max_length=120, blank=True, help_text="LxWxH")
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    categorias = models.ManyToManyField(Categoria, related_name="productos", blank=True)
    almacenes = models.ManyToManyField(Almacen, through="ArticuloAlmacen", related_name="productos", blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    meta_titulo = models.CharField(max_length=255, blank=True)
    meta_descripcion = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-creado_en"]

    @property
    def imagen_principal_url(self):
        imagen_principal = self.imagenes.filter(es_principal=True).first()
        if imagen_principal:
            return imagen_principal.image_url()
        # Opcional: devolver la primera imagen si ninguna es principal
        primera_imagen = self.imagenes.order_by('orden').first()
        if primera_imagen:
            return primera_imagen.image_url()
        return "" # O una URL a una imagen por defecto

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)[:240]
            slug = base
            counter = 1
            while Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def stock_total(self):
        agg = self.articulos_almacen.aggregate(total=models.Sum("cantidad"), reservado=models.Sum("reservado"))
        total = agg.get("total") or 0
        reservado = agg.get("reservado") or 0
        return max(0, total - reservado)


class ArticuloAlmacen(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="articulos_almacen")
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name="articulos")
    cantidad = models.IntegerField(default=0)
    reservado = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    lote = models.CharField(max_length=120, blank=True, null=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("producto", "almacen")
        ordering = ["-actualizado_en"]

    def disponible(self):
        return max(0, (self.cantidad or 0) - (self.reservado or 0))

    def __str__(self):
        return f"{self.producto.codigo} @ {self.almacen.codigo} = {self.cantidad}"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)

    imagen = models.URLField(max_length=500, blank=True, null=True)
    texto_alt = models.CharField(max_length=200, blank=True)
    es_principal = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def image_url(self):
        return self.imagen or ""
    
    def save(self, *args, **kwargs):
        if self.es_principal:
            ImagenProducto.objects.filter(producto=self.producto, es_principal=True).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Imagen {self.producto.codigo} ({'principal' if self.es_principal else 'secundaria'})"


class StockMovimiento(models.Model):
    TIPO_CHOICES = (
        ("entrada", "Entrada"),
        ("salida", "Salida"),
        ("ajuste", "Ajuste"),
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE, related_name="movimientos")
    cantidad = models.IntegerField()  # positivo para entradas, negativo para salidas
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    referencia = models.CharField(max_length=200, blank=True)
    comentario = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def clean(self):
        # Validaciones: cantidad > 0 y tipo coherente
        if self.cantidad is None or self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser un número positivo mayor que 0.")
        if self.tipo not in dict(self.TIPO_CHOICES):
            raise ValidationError("Tipo de movimiento inválido.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} {self.cantidad} {self.producto.codigo} @ {self.almacen.codigo}"
