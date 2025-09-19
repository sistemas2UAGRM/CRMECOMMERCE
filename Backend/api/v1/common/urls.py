# api/v1/common/urls.py

"""
📚 MICROCONCEPTOS - URLs PARA AUDITORÍA Y UTILIDADES

Los módulos comunes suelen incluir:

1. AUDITORÍA: Bitácora, logs, trazabilidad
2. UTILIDADES: Estadísticas, reportes, exportaciones
3. CONFIGURACIÓN: Parámetros del sistema

Consideraciones especiales:
- Solo lectura para datos de auditoría
- Permisos estrictos para información sensible
- Endpoints optimizados para grandes volúmenes
- Filtros avanzados para consultas complejas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BitacoraViewSet, BitacoraCreateView, BitacoraFilterView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Endpoints específicos para operaciones internas
    path('bitacora/create/', BitacoraCreateView.as_view(), name='bitacora-create'),
    path('bitacora/validate-filters/', BitacoraFilterView.as_view(), name='bitacora-validate-filters'),
]

"""
📝 MICROCONCEPTO: URLs para auditoría

Router genera automáticamente:

Consulta de Bitácora (solo lectura):
- GET /api/v1/common/bitacora/ -> BitacoraViewSet.list()
- GET /api/v1/common/bitacora/{id}/ -> BitacoraViewSet.retrieve()

Acciones personalizadas:
- GET /api/v1/common/bitacora/stats/ -> BitacoraViewSet.stats()
- GET /api/v1/common/bitacora/export/ -> BitacoraViewSet.export()

Endpoints específicos:
- POST /api/v1/common/bitacora/create/ -> BitacoraCreateView (uso interno)
- POST /api/v1/common/bitacora/validate-filters/ -> BitacoraFilterView

Ejemplos de filtros en URLs:
- GET /api/v1/common/bitacora/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31
- GET /api/v1/common/bitacora/?usuario_id=5&accion_contiene=login
- GET /api/v1/common/bitacora/?ip=192.168.1.100
- GET /api/v1/common/bitacora/?ordering=-fecha

Ejemplos de uso:
- GET /api/v1/common/bitacora/stats/ -> Estadísticas del sistema
- GET /api/v1/common/bitacora/export/?fecha_inicio=2024-01-01 -> Exportar datos
"""
