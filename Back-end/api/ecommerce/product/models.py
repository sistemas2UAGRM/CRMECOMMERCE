from django.db import models
from django.utils import timezone
from api.tenant.models import Tenant
from api.ecommerce.category.models import Categoria

class Producto(models.Model):
    name = models.CharField(max_length=127)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    stock_min = models.PositiveIntegerField(default=0)
    stock_actual = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ('tenant', 'name')

    def __str__(self):
        return f"{self.name}"
