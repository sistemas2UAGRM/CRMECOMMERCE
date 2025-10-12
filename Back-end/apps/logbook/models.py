from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from api.tenant.models import Tenant

User = get_user_model()

class Bitacora(models.Model):

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=128, null=False, blank=False)
    timestamp = models.DateTimeField(default=timezone.now)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.timestamp}: {self.user} - {self.action}"
