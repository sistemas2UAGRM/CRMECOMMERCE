# backend/apps/ecommerce/carritos/apps.py
from django.apps import AppConfig


class CarritosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ecommerce.carritos'

    def ready(self):
        # Importa los signals para que se registren en la app.
        import apps.ecommerce.carritos.signals
