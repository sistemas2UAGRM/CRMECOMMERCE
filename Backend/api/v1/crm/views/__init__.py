# api/v1/crm/views/__init__.py

"""
📚 VIEWS MODULARES PARA CRM

Este módulo organiza las views en archivos especializados:

- role_views.py: Gestión de roles
- permission_views.py: Gestión de permisos  
- user_role_views.py: Asignación de roles a usuarios

Beneficios:
- Separación clara de responsabilidades
- Archivos más pequeños y enfocados
- Fácil mantenimiento y escalabilidad
- Reutilización de servicios de negocio
"""

# Importar todas las views para mantener compatibilidad
from .role_views import RolViewSet
from .permission_views import PermissionViewSet
from .user_role_views import UserRoleViewSet

# Exportar views principales
__all__ = [
    'RolViewSet',
    'PermissionViewSet',
    'UserRoleViewSet'
]
