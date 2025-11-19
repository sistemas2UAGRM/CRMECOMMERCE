# backend/apps/ecommerce/pedidos/admin.py
from django.contrib import admin
from .models import Pedido, DetallePedido

class DetalleInline(admin.TabularInline):
    model = DetallePedido
    readonly_fields = ('nombre_producto', 'subtotal',)
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente', 'fecha_creacion', 'estado', 'total', 'pagado')
    search_fields = ('codigo', 'cliente__username', 'cliente__email')
    list_filter = ('estado', 'metodo_pago', 'pagado',)
    inlines = [DetalleInline]
