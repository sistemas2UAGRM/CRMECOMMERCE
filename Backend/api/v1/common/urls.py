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
    BitacoraViewSet, BitacoraFilterView, StatsView, ExportView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'bitacora', BitacoraViewSet, basename='bitacora')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Endpoints especializados
    path('bitacora/validate-filters/', BitacoraFilterView.as_view(), name='bitacora-validate-filters'),
    path('stats/', StatsView.as_view(), name='system-stats'),
    path('export/', ExportView.as_view(), name='data-export'),
]

"""
📝 MICROCONCEPTO: URLs modulares para Common

Router genera automáticamente estas URLs:

=== CONSULTA DE BITÁCORA (Solo lectura) ===
- GET /api/v1/common/bitacora/ -> BitacoraViewSet.list()
- GET /api/v1/common/bitacora/{id}/ -> BitacoraViewSet.retrieve()

Acciones personalizadas de bitácora:
- GET /api/v1/common/bitacora/recent_activity/?hours=24 -> BitacoraViewSet.recent_activity()
- GET /api/v1/common/bitacora/search/?q=login -> BitacoraViewSet.search()
- GET /api/v1/common/bitacora/user_summary/?user_id=5&days=30 -> BitacoraViewSet.user_summary()

=== VALIDACIÓN DE FILTROS ===
- POST /api/v1/common/bitacora/validate-filters/ -> BitacoraFilterView

=== ESTADÍSTICAS DEL SISTEMA ===
- GET /api/v1/common/stats/ -> StatsView (estadísticas generales)
- GET /api/v1/common/stats/?days=30 -> StatsView (estadísticas por usuario)

=== EXPORTACIÓN DE DATOS ===
- GET /api/v1/common/export/?format=json -> ExportView (exportar)
- POST /api/v1/common/export/ -> ExportView (validar exportación)

Ejemplos de filtros avanzados:
- GET /api/v1/common/bitacora/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31
- GET /api/v1/common/bitacora/?usuario_id=5&accion_contiene=login
- GET /api/v1/common/bitacora/?ip=192.168.1.100&objeto_tipo=Usuario
- GET /api/v1/common/bitacora/?ordering=-fecha&detalles_contiene=error

Ejemplos de estadísticas:
- GET /api/v1/common/stats/ -> Métricas generales del sistema
- GET /api/v1/common/stats/?days=7 -> Estadísticas de los últimos 7 días

Ejemplos de exportación:
- GET /api/v1/common/export/?format=csv&fecha_inicio=2024-01-01 -> Exportar como CSV
- GET /api/v1/common/export/?format=json&include_sensitive=true -> JSON con datos sensibles
"""
