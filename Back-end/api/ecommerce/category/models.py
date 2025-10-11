from django.db import models
from django.utils import timezone
from api.tenant.models import Tenant

class Categoria(models.Model):
    name = models.CharField(max_length=127)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('tenant', 'name')

    def __str__(self):
        return f"{self.name}"
