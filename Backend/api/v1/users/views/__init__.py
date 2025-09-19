# api/v1/users/views/__init__.py

"""
📚 VIEWS MODULARES PARA USUARIOS

Este módulo organiza las views en archivos especializados:

- auth_views.py: Autenticación (login, registro)
- profile_views.py: Gestión de perfil
- admin_views.py: Administración de usuarios
- search_views.py: Búsquedas y estadísticas

Beneficios:
- Archivos más pequeños y enfocados
- Fácil mantenimiento
- Mejor organización del código
- Escalabilidad mejorada
"""

# Importar todas las views para mantener compatibilidad
from .auth_views import (
    UserRegistrationView,
    AdminUserRegistrationView, 
    LoginView
)
from .profile_views import UserProfileViewSet
from .admin_views import UserAdminViewSet
from .search_views import UserSearchViewSet

# Mantener compatibilidad con imports existentes
__all__ = [
    'UserRegistrationView',
    'AdminUserRegistrationView',
    'LoginView',
    'UserProfileViewSet',
    'UserAdminViewSet', 
    'UserSearchViewSet'
]
