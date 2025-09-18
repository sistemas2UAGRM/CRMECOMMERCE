# core/common/models.py
from django.db import models
from django.conf import settings

class Bitacora(models.Model):
   accion = models.CharField(max_length=255)
   fecha = models.DateTimeField(auto_now_add=True)
   ip = models.GenericIPAddressField()
   usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

   
   def __str__(self):
      return f"{self.fecha} - {self.usuario} : {self.accion} | {self.ip}"