# api/v1/crm/services/__init__.py

from .role_service import RoleService
from .permission_service import PermissionService
from .user_role_service import UserRoleService

__all__ = ['RoleService', 'PermissionService', 'UserRoleService']
