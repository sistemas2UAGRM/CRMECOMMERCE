# api/v1/users/services/user_management_service.py

"""
📚 SERVICIO DE GESTIÓN DE USUARIOS

Este servicio encapsula la lógica de negocio para:
- Búsquedas de usuarios
- Estadísticas
- Filtros complejos
- Operaciones administrativas

Beneficios:
- Lógica centralizada
- Fácil testeo
- Reutilización en diferentes views
- Consistencia en operaciones
"""

from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from core.users.models import User
from django.contrib.auth.models import Group


class UserManagementService:
    """
    Servicio para operaciones de gestión de usuarios.
    """
    
    @staticmethod
    def search_users(query, user_requesting=None):
        """
        Buscar usuarios por término de búsqueda.
        
        Args:
            query (str): Término de búsqueda
            user_requesting (User): Usuario que hace la request (para permisos)
            
        Returns:
            QuerySet: Usuarios que coinciden con la búsqueda
        """
        if not query:
            return User.objects.none()
        
        # Construir consulta de búsqueda
        search_query = Q(username__icontains=query) | \
                      Q(email__icontains=query) | \
                      Q(first_name__icontains=query) | \
                      Q(last_name__icontains=query)
        
        queryset = User.objects.filter(search_query).order_by('username')
        
        # Aplicar filtros de permisos si es necesario
        if user_requesting:
            queryset = UserManagementService._apply_permission_filters(
                queryset, user_requesting
            )
        
        return queryset
    
    @staticmethod
    def get_active_users(user_requesting=None):
        """
        Obtener usuarios activos.
        
        Args:
            user_requesting (User): Usuario que hace la request
            
        Returns:
            QuerySet: Usuarios activos
        """
        queryset = User.objects.filter(is_active=True).order_by('username')
        
        if user_requesting:
            queryset = UserManagementService._apply_permission_filters(
                queryset, user_requesting
            )
        
        return queryset
    
    @staticmethod
    def get_users_by_role(role_name, user_requesting=None):
        """
        Obtener usuarios por rol específico.
        
        Args:
            role_name (str): Nombre del rol
            user_requesting (User): Usuario que hace la request
            
        Returns:
            dict: Información del rol y usuarios
        """
        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return {
                'error': f'Rol "{role_name}" no encontrado',
                'available_roles': list(Group.objects.values_list('name', flat=True))
            }
        
        users = User.objects.filter(groups=group).order_by('username')
        
        if user_requesting:
            users = UserManagementService._apply_permission_filters(
                users, user_requesting
            )
        
        return {
            'role': {
                'name': group.name,
                'total_users': users.count()
            },
            'users': users
        }
    
    @staticmethod
    def get_user_statistics(user_requesting=None):
        """
        Obtener estadísticas de usuarios.
        
        Args:
            user_requesting (User): Usuario que hace la request
            
        Returns:
            dict: Estadísticas del sistema
        """
        # Estadísticas básicas
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users
        
        # Usuarios por rol
        users_by_role = {}
        for group in Group.objects.all():
            count = User.objects.filter(groups=group).count()
            if count > 0:
                users_by_role[group.name] = count
        
        # Usuarios registrados en los últimos 30 días
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()
        
        # Usuarios con último login reciente (últimos 7 días)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_logins = User.objects.filter(
            last_login__gte=seven_days_ago
        ).count()
        
        # Usuarios sin roles asignados
        users_without_roles = User.objects.filter(groups__isnull=True).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'users_by_role': users_by_role,
            'recent_registrations_30d': recent_registrations,
            'recent_logins_7d': recent_logins,
            'users_without_roles': users_without_roles,
            'generated_at': timezone.now().isoformat()
        }
    
    @staticmethod
    def _apply_permission_filters(queryset, user_requesting):
        """
        Aplicar filtros basados en permisos del usuario.
        
        Args:
            queryset (QuerySet): QuerySet base
            user_requesting (User): Usuario que hace la request
            
        Returns:
            QuerySet: QuerySet filtrado según permisos
        """
        if not user_requesting or not user_requesting.is_authenticated:
            return queryset.none()
        
        user_groups = user_requesting.groups.values_list('name', flat=True)
        
        if 'administrador' in user_groups:
            # Administradores ven todos los usuarios
            return queryset
        elif 'empleadonivel1' in user_groups:
            # Supervisores ven empleados de nivel 2 y clientes
            allowed_groups = ['empleadonivel2', 'cliente']
            return queryset.filter(
                Q(groups__name__in=allowed_groups) | Q(id=user_requesting.id)
            ).distinct()
        elif 'empleadonivel2' in user_groups:
            # Empleados solo se ven a sí mismos y clientes
            return queryset.filter(
                Q(groups__name='cliente') | Q(id=user_requesting.id)
            ).distinct()
        else:
            # Clientes solo se ven a sí mismos
            return queryset.filter(id=user_requesting.id)
    
    @staticmethod
    def get_user_hierarchy_info(user):
        """
        Obtener información jerárquica del usuario.
        
        Args:
            user (User): Usuario
            
        Returns:
            dict: Información de jerarquía
        """
        groups = user.groups.values_list('name', flat=True)
        
        if 'administrador' in groups:
            level = 'admin'
            level_name = 'Administrador'
            can_manage = ['empleadonivel1', 'empleadonivel2', 'cliente']
        elif 'empleadonivel1' in groups:
            level = 'supervisor'
            level_name = 'Supervisor'
            can_manage = ['empleadonivel2', 'cliente']
        elif 'empleadonivel2' in groups:
            level = 'employee'
            level_name = 'Empleado'
            can_manage = ['cliente']
        elif 'cliente' in groups:
            level = 'client'
            level_name = 'Cliente'
            can_manage = []
        else:
            level = 'none'
            level_name = 'Sin rol'
            can_manage = []
        
        return {
            'level': level,
            'level_name': level_name,
            'groups': list(groups),
            'can_manage_roles': can_manage
        }

    @staticmethod
    def get_employees(user, search='', page=1, active_only=None, page_size=20):
        """
        Obtener empleados del sistema con paginación y filtros.
        
        Args:
            user (User): Usuario que hace la request
            search (str): Término de búsqueda
            page (int): Número de página
            active_only (bool|None): True=solo activos, False=solo inactivos, None=todos
            page_size (int): Tamaño de página
            
        Returns:
            dict: Empleados paginados
        """
        from django.core.paginator import Paginator
        
        # Roles de empleados (excluyendo clientes)
        employee_roles = ['administrador', 'empleadonivel1', 'empleadonivel2']
        
        # Query base para empleados
        queryset = User.objects.filter(
            groups__name__in=employee_roles
        ).distinct().order_by('first_name', 'last_name', 'username')
        
        # Filtrar por estado activo según el parámetro
        if active_only is True:
            queryset = queryset.filter(is_active=True)
        elif active_only is False:
            queryset = queryset.filter(is_active=False)
        # Si active_only es None, no filtramos por estado (mostramos todos)
        
        # Aplicar búsqueda si se proporciona
        if search:
            search_query = Q(username__icontains=search) | \
                          Q(email__icontains=search) | \
                          Q(first_name__icontains=search) | \
                          Q(last_name__icontains=search) | \
                          Q(celular__icontains=search)
            queryset = queryset.filter(search_query)
        
        # Aplicar filtros de permisos
        queryset = UserManagementService._apply_permission_filters(queryset, user)
        
        # Incluir información de grupos en la consulta
        queryset = queryset.prefetch_related('groups')
        
        # Paginar resultados
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        # Serializar empleados
        employees_data = []
        for employee in page_obj:
            employees_data.append({
                'id': employee.id,
                'username': employee.username,
                'email': employee.email,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'celular': employee.celular,
                'fecha_de_nacimiento': employee.fecha_de_nacimiento.isoformat() if employee.fecha_de_nacimiento else None,
                'sexo': employee.sexo,
                'is_active': employee.is_active,
                'date_joined': employee.date_joined.isoformat() if employee.date_joined else None,
                'groups': [
                    {
                        'id': group.id,
                        'name': group.name
                    } for group in employee.groups.all()
                ]
            })
        
        return {
            'count': paginator.count,
            'next': page_obj.has_next(),
            'previous': page_obj.has_previous(),
            'results': employees_data,
            'page': page,
            'num_pages': paginator.num_pages,
            'page_size': page_size
        }
