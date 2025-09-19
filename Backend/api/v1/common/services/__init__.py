# api/v1/common/services/__init__.py

"""
🔧 SERVICIOS MODULARES PARA COMMON

Este módulo centraliza la lógica de negocio para funcionalidades comunes:

Servicios implementados:
- BitacoraService: Gestión de auditoría y bitácora
- StatsService: Generación de estadísticas y reportes  
- ExportService: Funcionalidades de exportación de datos

Beneficios:
- Lógica de negocio centralizada y reutilizable
- Fácil testing y mantenimiento
- Separación clara entre views y lógica
- Preparado para microservicios futuros
"""

# Importar todos los servicios para facilitar el uso
from .bitacora_service import BitacoraService
from .stats_service import StatsService
from .export_service import ExportService

# Exportar servicios principales
__all__ = [
    'BitacoraService',
    'StatsService', 
    'ExportService'
]
