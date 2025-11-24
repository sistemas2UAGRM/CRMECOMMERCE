# backend/apps/tenants/models.py
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    """
    Representa al Ecommerce (El Inquilino).
    Cada cliente tendrá su propio ESQUEMA en la BD.
    """
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)
    # Aquí puedes agregar campos extra como 'plan_de_pago', 'logo', etc.
    # auto_create_schema = True (Por defecto es True)

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    """
    Representa el dominio web asociado al cliente.
    """
    def __str__(self):
        return self.domain