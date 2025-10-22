from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, DetallePedidoViewSet

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'detalles-pedido', DetallePedidoViewSet, basename='detallepedido')

urlpatterns = [
    path('', include(router.urls)),
]
