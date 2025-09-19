# api/v1/crm/urls.py

"""
📚 MICROCONCEPTOS - URLs PARA GESTIÓN DE ROLES Y PERMISOS

En un módulo CRM, las URLs deben reflejar las operaciones de negocio:

1. JERARQUÍA CLARA: /roles/, /permisos/, /assign-role/
2. ACCIONES ESPECÍFICAS: /roles/{id}/permissions/, /roles/{id}/users/
3. OPERACIONES COMPLEJAS: /assign-role/{user_id}/, /users-by-role/{role}/

Consideraciones de seguridad:
- Endpoints sensibles requieren permisos específicos
- URLs predictibles pero protegidas
- Versionado para cambios futuros
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RolViewSet, PermisoViewSet, AssignRoleView, UsersByRoleView
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'permisos', PermisoViewSet, basename='permiso')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
    
    # Endpoints específicos para operaciones complejas
    path('assign-role/<int:user_id>/', AssignRoleView.as_view(), name='assign-role'),
    path('users-by-role/<str:role_name>/', UsersByRoleView.as_view(), name='users-by-role'),
]

"""
📝 MICROCONCEPTO: URLs generadas para CRM

Router genera automáticamente:

Gestión de Roles:
- GET /api/v1/crm/roles/ -> RolViewSet.list()
- POST /api/v1/crm/roles/ -> RolViewSet.create()
- GET /api/v1/crm/roles/{id}/ -> RolViewSet.retrieve()
- PUT /api/v1/crm/roles/{id}/ -> RolViewSet.update()
- DELETE /api/v1/crm/roles/{id}/ -> RolViewSet.destroy()

Acciones personalizadas de roles:
- GET/PUT /api/v1/crm/roles/{id}/permissions/ -> RolViewSet.permissions()
- GET /api/v1/crm/roles/{id}/users/ -> RolViewSet.users()

Gestión de Permisos (solo lectura):
- GET /api/v1/crm/permisos/ -> PermisoViewSet.list()
- GET /api/v1/crm/permisos/{id}/ -> PermisoViewSet.retrieve()

Operaciones específicas:
- POST /api/v1/crm/assign-role/{user_id}/ -> AssignRoleView
- GET /api/v1/crm/users-by-role/{role_name}/ -> UsersByRoleView

Ejemplos de uso:
- GET /api/v1/crm/roles/1/permissions/ -> Ver permisos del rol 1
- PUT /api/v1/crm/roles/1/permissions/ -> Actualizar permisos del rol 1
- POST /api/v1/crm/assign-role/5/ -> Asignar roles al usuario 5
- GET /api/v1/crm/users-by-role/vendedor/ -> Ver usuarios con rol vendedor
"""
