# api/v1/urls.py

"""
 MICROCONCEPTOS - CONFIGURACIÓN PRINCIPAL DE API V1

Este archivo es el punto de entrada principal para la API v1.
Organiza todas las URLs de los diferentes módulos:

1. MODULARIDAD: Cada app tiene sus propias URLs
2. VERSIONADO: Facilita mantener múltiples versiones
3. ESCALABILIDAD: Fácil agregar nuevos módulos
4. MANTENIBILIDAD: Separación clara de responsabilidades

Estructura de URLs:
- /api/v1/users/ -> Gestión de usuarios
- /api/v1/crm/ -> Gestión de roles y permisos
- /api/v1/common/ -> Bitácora y utilidades
- /api/v1/ecommerce/ -> E-commerce (Sprint 1)
"""

from django.urls import path, include

urlpatterns = [
    # Módulo de usuarios (autenticación, perfiles, gestión)
    path('users/', include('api.v1.users.urls')),
    
    # Módulo CRM (roles, permisos, jerarquías)
    path('crm/', include('api.v1.crm.urls')),
    
    # Módulo común (bitácora, auditoría, utilidades)
    path('common/', include('api.v1.common.urls')),
    
    # Módulo e-commerce (productos, carritos, órdenes) - Sprint 1
    path('ecommerce/', include('api.v1.ecommerce.urls')),
]

"""
 MICROCONCEPTO: Estructura final de URLs

La API v1 queda organizada así:

AUTENTICACIÓN Y USUARIOS:
- POST /api/v1/users/register/ -> Registro público
- POST /api/v1/users/admin-register/ -> Registro por admin
- POST /api/v1/users/login/ -> Login con JWT
- GET /api/v1/users/profile/ -> Perfil del usuario actual
- GET /api/v1/users/ -> Listar usuarios
- GET /api/v1/users/active/ -> Usuarios activos
- GET /api/v1/users/search/?q=juan -> Buscar usuarios
- GET /api/v1/users/stats/ -> Estadísticas de usuarios
- GET /api/v1/users/by-role/vendedor/ -> Usuarios por rol

GESTIÓN CRM:
- GET /api/v1/crm/roles/ -> Listar roles
- GET /api/v1/crm/roles/1/permissions/ -> Permisos de un rol
- PUT /api/v1/crm/roles/1/permissions/ -> Actualizar permisos
- POST /api/v1/crm/assign-role/5/ -> Asignar roles a usuario
- GET /api/v1/crm/users-by-role/administrador/ -> Usuarios por rol
- GET /api/v1/crm/permisos/ -> Listar permisos disponibles

AUDITORÍA Y BITÁCORA:
- GET /api/v1/common/bitacora/ -> Consultar bitácora
- GET /api/v1/common/bitacora/stats/ -> Estadísticas de auditoría
- GET /api/v1/common/bitacora/export/ -> Exportar registros
- POST /api/v1/common/bitacora/create/ -> Crear registro (interno)

Filtros comunes:
- ?ordering=-fecha -> Ordenar por fecha descendente
- ?fecha_inicio=2024-01-01&fecha_fin=2024-01-31 -> Rango de fechas
- ?usuario_id=5 -> Filtrar por usuario
- ?page=2&page_size=20 -> Paginación
"""