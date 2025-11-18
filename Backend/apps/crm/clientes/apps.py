# apps/crm/clientes/apps.py
from django.apps import AppConfig

class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crm.clientes'

    def ready(self):
        import apps.crm.clientes.signals
