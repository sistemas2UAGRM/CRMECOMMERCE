# /apps/ecommerce/pagos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PagoViewSet, StripeWebhookView

router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    path('', include(router.urls)),
    # URL que debes configurar en tu dashboard de Stripe
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
]