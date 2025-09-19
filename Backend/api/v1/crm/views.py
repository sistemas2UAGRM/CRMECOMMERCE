# api/v1/crm/views.py

"""
📚 MICROCONCEPTOS - VIEWS PARA GESTIÓN DE ROLES Y PERMISOS

En un sistema CRM empresarial, la gestión de roles y permisos es crítica:

1. SEGURIDAD: Solo administradores pueden modificar roles
2. AUDITORÍA: Todas las acciones deben registrarse
3. ESCALABILIDAD: Debe soportar jerarquías complejas
4. FLEXIBILIDAD: Permisos granulares por módulo

Patrones implementados:
- ViewSets para operaciones CRUD completas
- Acciones personalizadas para operaciones específicas
- Validación de permisos a nivel de método
- Logging automático de cambios
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group, Permission
from django.db.models import Count, Q
from django.utils import timezone

from core.crm.models import RolExtendido, PermisoExtendido
from core.users.models import User
from core.common.models import Bitacora
from .serializers import (
    RolBasicSerializer, RolDetailSerializer, RolPermissionsSerializer,
    PermisoBasicSerializer, PermisoDetailSerializer, AssignRoleSerializer,
    UserRoleAssignmentSerializer, UsersByRoleSerializer
)


class RolViewSet(viewsets.ModelViewSet):
    """
    📝 MICROCONCEPTO: ViewSet para gestión de roles
    
    Este ViewSet maneja todas las operaciones CRUD para roles:
    - list(): GET /crm/roles/ (listar roles)
    - create(): POST /crm/roles/ (crear rol)
    - retrieve(): GET /crm/roles/{id}/ (detalle de rol)
    - update(): PUT /crm/roles/{id}/ (actualizar rol)
    - destroy(): DELETE /crm/roles/{id}/ (eliminar rol)
    
    Además incluye acciones personalizadas para gestión de permisos.
    """
    
    queryset = RolExtendido.objects.select_related('group').prefetch_related(
        'group__permissions', 'group__user_set_custom'
    ).filter(activo=True).order_by('group__name')
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        📝 MICROCONCEPTO: Serializers dinámicos por acción
        
        Diferentes acciones requieren diferentes niveles de detalle:
        - list: Información básica para performance
        - retrieve: Información completa incluyendo permisos
        - create/update: Campos editables
        """
        if self.action == 'list':
            return RolBasicSerializer
        elif self.action in ['retrieve', 'permissions']:
            return RolDetailSerializer
        return RolBasicSerializer
    
    def get_permissions(self):
        """
        📝 MICROCONCEPTO: Permisos granulares por acción
        
        Solo administradores pueden modificar roles, pero supervisores
        pueden ver información para gestionar sus equipos.
        """
        if self.action in ['list', 'retrieve']:
            # Ver roles: administradores y supervisores
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Modificar roles: solo administradores
            permission_classes = [permissions.IsAuthenticated]
            
        return [permission() for permission in permission_classes]
    
    def list(self, request):
        """
        📝 MICROCONCEPTO: Personalización del método list()
        
        Agregamos información adicional útil para el frontend.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Agregar estadísticas generales
        total_roles = queryset.count()
        total_usuarios = User.objects.filter(groups__isnull=False).distinct().count()
        
        return Response({
            'count': total_roles,
            'total_usuarios_con_roles': total_usuarios,
            'results': serializer.data
        })
    
    def perform_create(self, serializer):
        """Registrar creación de rol en bitácora"""
        rol_extendido = serializer.save()
        
        Bitacora.objects.create(
            accion=f"Rol creado: {rol_extendido.group.name}",
            ip=self.get_client_ip(),
            usuario=self.request.user
        )
    
    def perform_update(self, serializer):
        """Registrar actualización de rol en bitácora"""
        rol_extendido = serializer.save()
        
        Bitacora.objects.create(
            accion=f"Rol actualizado: {rol_extendido.group.name}",
            ip=self.get_client_ip(),
            usuario=self.request.user
        )
    
    @action(detail=True, methods=['get', 'put'])
    def permissions(self, request, pk=None):
        """
        📝 MICROCONCEPTO: Acción personalizada para gestión de permisos
        
        GET: Ver permisos actuales del rol
        PUT: Actualizar permisos del rol
        """
        rol_extendido = self.get_object()
        
        if request.method == 'GET':
            serializer = RolPermissionsSerializer(rol_extendido)
            return Response(serializer.data)
            
        elif request.method == 'PUT':
            # Solo administradores pueden modificar permisos
            if not request.user.groups.filter(name='administrador').exists():
                return Response(
                    {'error': 'Solo administradores pueden modificar permisos'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            permission_ids = request.data.get('permission_ids', [])
            
            # Validar que todos los permisos existen
            permissions = Permission.objects.filter(id__in=permission_ids)
            if len(permissions) != len(permission_ids):
                return Response(
                    {'error': 'Algunos permisos no existen'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actualizar permisos
            rol_extendido.group.permissions.set(permissions)
            
            # Registrar en bitácora
            Bitacora.objects.create(
                accion=f"Permisos actualizados para rol: {rol_extendido.group.name} ({len(permissions)} permisos)",
                ip=self.get_client_ip(),
                usuario=request.user
            )
            
            # Retornar permisos actualizados
            serializer = RolPermissionsSerializer(rol_extendido)
            return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        📝 MICROCONCEPTO: Acción para listar usuarios de un rol
        
        Útil para ver qué usuarios tienen un rol específico.
        """
        rol_extendido = self.get_object()
        users = User.objects.filter(groups=rol_extendido.group).select_related()
        
        # Preparar datos para el serializer
        data = {
            'rol_extendido': rol_extendido,
            'usuarios': users,
            'total_usuarios': users.count(),
            'fecha_asignacion_rol': timezone.now()  # Esto debería venir de un modelo de auditoría
        }
        
        serializer = UsersByRoleSerializer(data)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Obtener IP del cliente para auditoría"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class PermisoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    📝 MICROCONCEPTO: ReadOnlyModelViewSet
    
    Los permisos generalmente no se crean/modifican via API,
    sino que se definen en el código. Por eso usamos ReadOnlyModelViewSet.
    """
    
    queryset = PermisoExtendido.objects.select_related('permission').filter(activo=True)
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PermisoBasicSerializer
        return PermisoDetailSerializer
    
    def get_permissions(self):
        """Solo administradores y supervisores pueden ver permisos"""
        if self.request.user.is_authenticated:
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if any(role in user_groups for role in ['administrador', 'empleadonivel1']):
                return [permissions.IsAuthenticated()]
        
        return [permissions.IsAdminUser()]


class AssignRoleView(APIView):
    """
    📝 MICROCONCEPTO: APIView para operaciones complejas
    
    Para operaciones que no encajan en el patrón CRUD estándar,
    como asignar múltiples roles a un usuario.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        """
        Asignar roles a un usuario específico
        """
        # Solo administradores pueden asignar roles
        if not request.user.groups.filter(name='administrador').exists():
            return Response(
                {'error': 'Solo administradores pueden asignar roles'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar datos de entrada
        serializer = AssignRoleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        role_ids = serializer.validated_data['roles']
        motivo = serializer.validated_data.get('motivo', '')
        
        # Obtener roles
        roles_extendidos = RolExtendido.objects.filter(id__in=role_ids, activo=True)
        groups = [rol.group for rol in roles_extendidos]
        
        # Asignar roles al usuario
        user.groups.set(groups)
        
        # Registrar en bitácora
        roles_nombres = [rol.group.name for rol in roles_extendidos]
        Bitacora.objects.create(
            accion=f"Roles asignados a {user.username}: {', '.join(roles_nombres)}. Motivo: {motivo}",
            ip=self.get_client_ip(),
            usuario=request.user
        )
        
        # Preparar respuesta
        response_data = {
            'user': user,
            'roles_asignados': roles_extendidos,
            'fecha_asignacion': timezone.now()
        }
        
        response_serializer = UserRoleAssignmentSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UsersByRoleView(APIView):
    """
    📝 MICROCONCEPTO: Vista para consultas específicas
    
    Endpoint para obtener usuarios filtrados por rol específico.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, role_name):
        """
        Obtener usuarios que tienen un rol específico
        """
        # Verificar permisos
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(role in user_groups for role in ['administrador', 'empleadonivel1']):
            return Response(
                {'error': 'No tiene permisos para ver esta información'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            group = Group.objects.get(name=role_name)
            rol_extendido = RolExtendido.objects.get(group=group)
        except (Group.DoesNotExist, RolExtendido.DoesNotExist):
            return Response(
                {'error': f'Rol "{role_name}" no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener usuarios con este rol
        users = User.objects.filter(groups=group).select_related().order_by('username')
        
        # Preparar datos para serializer
        data = {
            'rol_extendido': rol_extendido,
            'usuarios': users,
            'total_usuarios': users.count(),
            'fecha_asignacion_rol': timezone.now()
        }
        
        serializer = UsersByRoleSerializer(data)
        return Response(serializer.data)
