# /apps/ecommerce/pagos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PagoViewSet, StripeWebhookView, CrearPaymentIntentView, VerificarEstadoPagoView

router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    path('', include(router.urls)),
    # Endpoint para crear PaymentIntent
    path('crear-payment-intent/', CrearPaymentIntentView.as_view(), name='crear-payment-intent'),
    # Endpoint para verificar estado del pago (llamar desde mobile después de confirmación)
    path('verificar-estado-pago/', VerificarEstadoPagoView.as_view(), name='verificar-estado-pago'),
    # Webhook de Stripe (para producción o desarrollo con Stripe CLI)
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
]