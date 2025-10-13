from django.db import models
from django.utils import timezone

class Tenant(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    REQUIRED_FIELDS = ['name', 'domain']

    def __str__(self):
        return self.domain
