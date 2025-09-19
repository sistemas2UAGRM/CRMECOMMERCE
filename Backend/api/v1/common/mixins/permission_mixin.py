# api/v1/common/mixins/permission_mixin.py

"""
📚 MIXIN PARA PERMISOS REUTILIZABLES

Este mixin proporciona métodos comunes para validación de permisos
basados en roles jerárquicos del sistema.

Jerarquía de roles:
- administrador: Acceso completo
- empleadonivel1: Supervisor (gestión de equipo)
- empleadonivel2: Vendedor (operaciones básicas)
- cliente: Acceso limitado
"""

from rest_framework import permissions
from django.contrib.auth.models import Group


class PermissionMixin:
    """
    Mixin para validaciones de permisos comunes basados en roles.
    
    Uso:
        class MiViewSet(PermissionMixin, viewsets.ModelViewSet):
            def get_permissions(self):
                if self.action == 'create':
                    return self.admin_or_supervisor_permission()
                return super().get_permissions()
    """
    
    def is_admin(self, user=None):
        """Verificar si el usuario es administrador"""
        user = user or getattr(self, 'request', None) and self.request.user
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name='administrador').exists()
    
    def is_supervisor(self, user=None):
        """Verificar si el usuario es supervisor (empleadonivel1)"""
        user = user or getattr(self, 'request', None) and self.request.user
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name='empleadonivel1').exists()
    
    def is_employee(self, user=None):
        """Verificar si el usuario es empleado (empleadonivel2)"""
        user = user or getattr(self, 'request', None) and self.request.user
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name='empleadonivel2').exists()
    
    def is_client(self, user=None):
        """Verificar si el usuario es cliente"""
        user = user or getattr(self, 'request', None) and self.request.user
        if not user or not user.is_authenticated:
            return False
        return user.groups.filter(name='cliente').exists()
    
    def is_admin_or_supervisor(self, user=None):
        """Verificar si el usuario es admin o supervisor"""
        return self.is_admin(user) or self.is_supervisor(user)
    
    def is_employee_or_above(self, user=None):
        """Verificar si el usuario es empleado o rango superior"""
        return self.is_admin(user) or self.is_supervisor(user) or self.is_employee(user)
    
    def get_user_role_level(self, user=None):
        """
        Obtener nivel numérico del rol del usuario.
        Útil para comparaciones jerárquicas.
        
        Returns:
            int: 4=admin, 3=supervisor, 2=employee, 1=client, 0=no_auth
        """
        user = user or getattr(self, 'request', None) and self.request.user
        if not user or not user.is_authenticated:
            return 0
        
        if self.is_admin(user):
            return 4
        elif self.is_supervisor(user):
            return 3
        elif self.is_employee(user):
            return 2
        elif self.is_client(user):
            return 1
        return 0
    
    # Métodos para obtener clases de permisos
    def admin_only_permission(self):
        """Permisos solo para administradores"""
        return [permissions.IsAuthenticated(), AdminOnlyPermission()]
    
    def admin_or_supervisor_permission(self):
        """Permisos para administradores y supervisores"""
        return [permissions.IsAuthenticated(), AdminOrSupervisorPermission()]
    
    def employee_or_above_permission(self):
        """Permisos para empleados y superiores"""
        return [permissions.IsAuthenticated(), EmployeeOrAbovePermission()]
    
    def authenticated_permission(self):
        """Permisos para usuarios autenticados"""
        return [permissions.IsAuthenticated()]


# Clases de permisos personalizadas
class AdminOnlyPermission(permissions.BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='administrador').exists()


class AdminOrSupervisorPermission(permissions.BasePermission):
    """Permiso para administradores y supervisores"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(
            name__in=['administrador', 'empleadonivel1']
        ).exists()


class EmployeeOrAbovePermission(permissions.BasePermission):
    """Permiso para empleados y superiores"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(
            name__in=['administrador', 'empleadonivel1', 'empleadonivel2']
        ).exists()
