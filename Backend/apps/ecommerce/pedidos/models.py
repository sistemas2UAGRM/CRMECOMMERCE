# backend/apps/ecommerce/pedidos/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

from ..productos.models import Producto

User = settings.AUTH_USER_MODEL

class Pedido(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_PAGADO = 'pagado'
    ESTADO_ENVIADO = 'enviado'
    ESTADO_CANCELADO = 'cancelado'
    ESTADO_ENTREGADO = 'entregado'

    ESTADOS = [
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_PAGADO, 'Pagado'),
        (ESTADO_ENVIADO, 'Enviado'),
        (ESTADO_ENTREGADO, 'Entregado'),
        (ESTADO_CANCELADO, 'Cancelado'),
    ]

    METODO_TARJETA = 'tarjeta'
    METODO_TRANSFERENCIA = 'transferencia'
    METODO_EFECTIVO = 'efectivo'
    METODO_PAYPAL = 'paypal'

    METODOS_PAGO = [
        (METODO_TARJETA, 'Tarjeta'),
        (METODO_TRANSFERENCIA, 'Transferencia bancaria'),
        (METODO_EFECTIVO, 'Efectivo'),
        (METODO_PAYPAL, 'PayPal'),
    ]

    codigo = models.CharField(max_length=50, unique=True, help_text="Código de pedido (ej: PED-0001)")
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    metodo_pago = models.CharField(max_length=30, choices=METODOS_PAGO, null=True, blank=True)
    direccion_envio = models.TextField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    comentario = models.TextField(blank=True, null=True)
    enviado = models.BooleanField(default=False)
    pagado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"{self.codigo} - {self.cliente or 'Anónimo'}"

    def calcular_totales(self, impuesto_rate=0.0):
        """
        Recalcula subtotal, impuestos y total en base a sus detalles.
        impuesto_rate = porcentaje decimal (ej: 0.18 para 18%)
        """
        detalles = self.detalles.all()
        subtotal = sum([d.subtotal for d in detalles])
        impuestos = subtotal * Decimal(impuesto_rate)  # Convertir impuesto_rate a Decimal
        total = subtotal + impuestos
        self.subtotal = subtotal
        self.impuestos = round(impuestos, 2)
        self.total = round(total, 2)
        return self.subtotal, self.impuestos, self.total


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    nombre_producto = models.CharField(max_length=255)  # captura el nombre al momento del pedido
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    def calcular_subtotal(self):
        # Convertir descuento a Decimal para evitar errores de tipo
        descuento_decimal = Decimal(str(self.descuento)) if self.descuento else Decimal('0.00')
        subtotal = (self.precio_unitario * self.cantidad) - descuento_decimal
        self.subtotal = round(subtotal, 2)
        return self.subtotal
