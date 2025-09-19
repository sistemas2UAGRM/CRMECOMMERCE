# api/v1/users/urls.py

"""
📚 URLs MODULARES PARA USUARIOS

Nueva estructura modular que organiza las URLs por funcionalidad:

AUTENTICACIÓN:
- /register/ -> Registro público
- /admin-register/ -> Registro por admin
- /login/ -> Login JWT

PERFIL:
- /profile/me/ -> Ver/actualizar perfil
- /profile/permissions/ -> Ver permisos
- /profile/change-password/ -> Cambiar contraseña

ADMINISTRACIÓN:
- /admin/ -> CRUD usuarios (admin only)
- /admin/{id}/activate/ -> Activar usuario
- /admin/{id}/deactivate/ -> Desactivar usuario

BÚSQUEDA:
- /search/search/ -> Buscar usuarios
- /search/active/ -> Usuarios activos
- /search/by-role/{role}/ -> Usuarios por rol
- /search/stats/ -> Estadísticas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar views modulares
from .views import (
    # Autenticación
    UserRegistrationView,
    AdminUserRegistrationView,
    LoginView,
    # Módulos especializados
    UserProfileViewSet,
    UserAdminViewSet,
    UserSearchViewSet
)

# Routers para cada módulo
profile_router = DefaultRouter()
profile_router.register(r'profile', UserProfileViewSet, basename='user-profile')

admin_router = DefaultRouter()
admin_router.register(r'admin', UserAdminViewSet, basename='user-admin')

search_router = DefaultRouter()
search_router.register(r'search', UserSearchViewSet, basename='user-search')

urlpatterns = [
    # === AUTENTICACIÓN (endpoints públicos) ===
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('admin-register/', AdminUserRegistrationView.as_view(), name='admin-user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    
    # === PERFIL (gestión personal) ===
    path('', include(profile_router.urls)),
    
    # === ADMINISTRACIÓN (solo admins) ===
    path('', include(admin_router.urls)),
    
    # === BÚSQUEDA Y ESTADÍSTICAS ===
    path('', include(search_router.urls)),
]

"""
📝 ENDPOINTS RESULTANTES:

AUTENTICACIÓN:
- POST /api/v1/users/register/
- POST /api/v1/users/admin-register/
- POST /api/v1/users/login/

PERFIL:
- GET/PUT/PATCH /api/v1/users/profile/me/
- GET /api/v1/users/profile/permissions/
- POST /api/v1/users/profile/change-password/

ADMINISTRACIÓN:
- GET /api/v1/users/admin/ (listar usuarios)
- POST /api/v1/users/admin/ (crear usuario)
- GET /api/v1/users/admin/{id}/ (detalle usuario)
- PUT/PATCH /api/v1/users/admin/{id}/ (actualizar usuario)
- DELETE /api/v1/users/admin/{id}/ (eliminar usuario)
- POST /api/v1/users/admin/{id}/activate/
- POST /api/v1/users/admin/{id}/deactivate/
- GET /api/v1/users/admin/{id}/activity_log/

BÚSQUEDA:
- GET /api/v1/users/search/search/?q=term
- GET /api/v1/users/search/active/
- GET /api/v1/users/search/by-role/{role_name}/
- GET /api/v1/users/search/stats/
- GET /api/v1/users/search/roles/
- GET /api/v1/users/search/hierarchy/
"""
