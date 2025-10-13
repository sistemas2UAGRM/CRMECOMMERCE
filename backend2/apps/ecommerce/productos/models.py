from django.db import models

from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal

class Categoria(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Categorias"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    """
    Representa un almacén / ubicación física (warehouse).
    Los productos estarán relacionados many-to-many con Inventory
    a través de InventoryItem, que guarda cantidad y metadatos.
    """
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Producto(models.Model):
    codigo = models.CharField(max_length=64, unique=True, help_text="Stock Keeping Unit")
    nombre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0.00"))])
    currency = models.CharField(max_length=10, default="USD")
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.CharField(max_length=120, blank=True, help_text="LxWxH or dimensions text")
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    categories = models.ManyToManyField(Category, related_name="products", blank=True)
    inventories = models.ManyToManyField(Inventory, through="InventoryItem", related_name="products", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # metadatos SEO
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:240]
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    def total_stock(self):
        agg = self.inventoryitem_set.aggregate(total=models.Sum("quantity"))
        return agg["total"] or 0


class InventoryItem(models.Model):
    """
    Through table between Product y Inventory:
    contiene cantidad, estado, lote, fecha de expiracion, etc.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    batch = models.CharField(max_length=120, blank=True, null=True)
    expiration_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "inventory")
        ordering = ["-updated_at"]

    def available(self):
        return max(0, self.quantity - (self.reserved or 0))

    def __str__(self):
        return f"{self.product.sku} @ {self.inventory.code} = {self.quantity}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/%Y/%m/%d/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image {self.product.sku} ({'main' if self.is_main else 'aux'})"
