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
    RolViewSet, PermissionViewSet, UserRoleViewSet
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')

urlpatterns = [
    # ViewSet URLs
    path('', include(router.urls)),
]

"""
📝 MICROCONCEPTO: URLs modulares para CRM

Router genera automáticamente estas URLs:

=== GESTIÓN DE ROLES ===
- GET /api/v1/crm/roles/ -> RolViewSet.list()
- POST /api/v1/crm/roles/ -> RolViewSet.create()
- GET /api/v1/crm/roles/{id}/ -> RolViewSet.retrieve()
- PUT /api/v1/crm/roles/{id}/ -> RolViewSet.update()
- DELETE /api/v1/crm/roles/{id}/ -> RolViewSet.destroy()

Acciones personalizadas de roles:
- GET /api/v1/crm/roles/{id}/permissions/ -> RolViewSet.permissions()
- POST /api/v1/crm/roles/{id}/assign_permissions/ -> RolViewSet.assign_permissions()
- GET /api/v1/crm/roles/{id}/users/ -> RolViewSet.users()
- GET /api/v1/crm/roles/search/?q=query -> RolViewSet.search()
- GET /api/v1/crm/roles/stats/ -> RolViewSet.stats()

=== GESTIÓN DE PERMISOS (Solo lectura) ===
- GET /api/v1/crm/permissions/ -> PermissionViewSet.list()
- GET /api/v1/crm/permissions/{id}/ -> PermissionViewSet.retrieve()

Acciones personalizadas de permisos:
- GET /api/v1/crm/permissions/by_app/ -> PermissionViewSet.by_app()
- GET /api/v1/crm/permissions/by_model/?app_label=&model= -> PermissionViewSet.by_model()
- GET /api/v1/crm/permissions/search/?q=query -> PermissionViewSet.search()
- GET /api/v1/crm/permissions/stats/ -> PermissionViewSet.stats()
- GET /api/v1/crm/permissions/apps/ -> PermissionViewSet.apps()
- GET /api/v1/crm/permissions/models/?app_label= -> PermissionViewSet.models()

=== GESTIÓN DE ASIGNACIONES USUARIO-ROL ===
- POST /api/v1/crm/user-roles/assign_role/ -> UserRoleViewSet.assign_role()
- POST /api/v1/crm/user-roles/remove_role/ -> UserRoleViewSet.remove_role()
- GET /api/v1/crm/user-roles/user/{user_id}/roles/ -> UserRoleViewSet.user_roles()
- GET /api/v1/crm/user-roles/role/{role_id}/users/ -> UserRoleViewSet.role_users()
- POST /api/v1/crm/user-roles/bulk_assign/ -> UserRoleViewSet.bulk_assign()
- POST /api/v1/crm/user-roles/bulk_remove/ -> UserRoleViewSet.bulk_remove()
- GET /api/v1/crm/user-roles/stats/ -> UserRoleViewSet.stats()
- GET /api/v1/crm/user-roles/validate_assignment/?user_id=&role_id= -> UserRoleViewSet.validate_assignment()

Ejemplos de uso:
- GET /api/v1/crm/roles/1/permissions/ -> Ver permisos del rol 1
- POST /api/v1/crm/roles/1/assign_permissions/ -> Asignar permisos al rol 1
- POST /api/v1/crm/user-roles/assign_role/ -> Asignar rol a usuario
- GET /api/v1/crm/permissions/by_app/ -> Ver permisos agrupados por aplicación
"""
