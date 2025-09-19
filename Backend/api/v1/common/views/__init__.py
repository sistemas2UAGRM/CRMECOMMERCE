# api/v1/common/views/__init__.py

"""
📚 VIEWS MODULARES PARA COMMON

Este módulo organiza las views en archivos especializados:

- bitacora_views.py: Gestión de auditoría y consulta de bitácora
- stats_views.py: Generación de estadísticas y métricas
- export_views.py: Funcionalidades de exportación de datos

Beneficios:
- Separación clara de responsabilidades
- Archivos más pequeños y enfocados
- Fácil mantenimiento y escalabilidad
- Reutilización de servicios de negocio
"""

# Importar todas las views para mantener compatibilidad
from .bitacora_views import BitacoraViewSet, BitacoraFilterView
from .stats_views import StatsView
from .export_views import ExportView

# Exportar views principales
__all__ = [
    'BitacoraViewSet',
    'BitacoraFilterView',
    'StatsView',
    'ExportView'
]
