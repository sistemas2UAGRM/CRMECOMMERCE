# core/crm/models.py
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.conf import settings

# Nota: Usamos el sistema de permisos nativo de Django
# Group = Rol en nuestro diagrama
# Permission = Permiso en nuestro diagrama  
# Group.permissions = Relación muchos a muchos entre Rol y Permiso

# Si necesitamos extender funcionalidad, podemos crear proxies o relaciones adicionales
class RolExtendido(models.Model):
    """
    Extiende el modelo Group de Django para agregar funcionalidad específica del CRM
    """
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='rol_extendido')
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rol: {self.group.name}"
    
    class Meta:
        verbose_name = "Rol Extendido"
        verbose_name_plural = "Roles Extendidos"


class PermisoExtendido(models.Model):
    """
    Extiende el modelo Permission de Django para agregar funcionalidad específica del CRM
    """
    permission = models.OneToOneField(Permission, on_delete=models.CASCADE, related_name='permiso_extendido')
    descripcion_detallada = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=100, help_text="Módulo al que pertenece (CRM, Ecommerce, etc.)")
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Permiso: {self.permission.name}"
    
    class Meta:
        verbose_name = "Permiso Extendido"
        verbose_name_plural = "Permisos Extendidos"
