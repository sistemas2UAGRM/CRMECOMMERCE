# api/v1/common/mixins/__init__.py

from .audit_mixin import AuditMixin
from .permission_mixin import PermissionMixin
from .ip_mixin import IPMixin

__all__ = ['AuditMixin', 'PermissionMixin', 'IPMixin']
