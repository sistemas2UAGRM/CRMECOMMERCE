# /apps/ecommerce/pagos/models.py
from django.db import models
from ..pedidos.models import Pedido

class Pago(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_EXITOSO = 'exitoso'
    ESTADO_FALLIDO = 'fallido'
    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_EXITOSO, 'Exitoso'),
        (ESTADO_FALLIDO, 'Fallido'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='pagos')
    proveedor = models.CharField(max_length=50, default='stripe', help_text="Ej: stripe, paypal")
    id_transaccion_proveedor = models.CharField(max_length=255, unique=True, help_text="ID de la transacción en el proveedor de pagos")
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=10, default='USD')
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    
    # Guarda la respuesta completa del proveedor para auditoría
    datos_respuesta = models.JSONField(blank=True, null=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago {self.id_transaccion_proveedor} para Pedido {self.pedido.codigo} - {self.estado}"