# api/v1/users/views_legacy_compatible.py

"""
📚 COMPATIBILIDAD CON VIEWS LEGACY

Este archivo mantiene compatibilidad con imports existentes durante la transición.
Una vez que todo el código use la nueva estructura modular, este archivo puede eliminarse.

IMPORTANTE: Este es un archivo temporal de transición.
"""

# Importar desde la nueva estructura modular
from .views import (
    UserRegistrationView,
    AdminUserRegistrationView,
    LoginView,
    UserProfileViewSet,
    UserAdminViewSet,
    UserSearchViewSet
)

# Crear una clase combinada para mantener compatibilidad con el UserViewSet original
class UserViewSet(UserAdminViewSet):
    """
    CLASE DE COMPATIBILIDAD - NO USAR EN CÓDIGO NUEVO
    
    Esta clase combina funcionalidades para mantener compatibilidad 
    con el UserViewSet original monolítico.
    
    ⚠️ DEPRECATED: Use las nuevas views modulares:
    - UserProfileViewSet para gestión de perfil
    - UserAdminViewSet para administración
    - UserSearchViewSet para búsquedas
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Log de advertencia para migración
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "UserViewSet monolítico está deprecated. "
            "Migre a UserProfileViewSet, UserAdminViewSet o UserSearchViewSet"
        )
    
    # Agregar métodos desde UserSearchViewSet para compatibilidad
    def search(self, request):
        """Delegado a UserSearchViewSet"""
        search_viewset = UserSearchViewSet()
        search_viewset.request = request
        search_viewset.format_kwarg = None
        return search_viewset.search(request)
    
    def active(self, request):
        """Delegado a UserSearchViewSet"""
        search_viewset = UserSearchViewSet()
        search_viewset.request = request
        search_viewset.format_kwarg = None
        return search_viewset.active(request)
    
    def by_role(self, request, role_name=None):
        """Delegado a UserSearchViewSet"""
        search_viewset = UserSearchViewSet()
        search_viewset.request = request
        search_viewset.format_kwarg = None
        return search_viewset.by_role(request, role_name)
    
    def stats(self, request):
        """Delegado a UserSearchViewSet"""
        search_viewset = UserSearchViewSet()
        search_viewset.request = request
        search_viewset.format_kwarg = None
        return search_viewset.stats(request)
    
    # Agregar métodos desde UserProfileViewSet para compatibilidad
    def profile(self, request):
        """Delegado a UserProfileViewSet"""
        profile_viewset = UserProfileViewSet()
        profile_viewset.request = request
        profile_viewset.format_kwarg = None
        return profile_viewset.me(request)


# Exportar todo para mantener compatibilidad
__all__ = [
    'UserViewSet',  # Clase de compatibilidad
    'UserRegistrationView',
    'AdminUserRegistrationView', 
    'LoginView',
    # Nuevas clases modulares
    'UserProfileViewSet',
    'UserAdminViewSet',
    'UserSearchViewSet'
]
