
# api/v1/users/views.py

"""
📚 MICROCONCEPTOS - DJANGO REST FRAMEWORK VIEWS

DRF proporciona varias clases base para views:

1. APIView: Clase base más básica, máximo control
2. GenericAPIView: Añade funcionalidad común (queryset, serializer_class, etc.)
3. ViewSets: Agrupan lógica relacionada (list, create, retrieve, update, destroy)
4. ModelViewSet: ViewSet completo para operaciones CRUD
5. ReadOnlyModelViewSet: Solo operaciones de lectura (list, retrieve)

Mixins disponibles:
- ListModelMixin: GET /resource/ (listar)
- CreateModelMixin: POST /resource/ (crear)
- RetrieveModelMixin: GET /resource/{id}/ (detalle)
- UpdateModelMixin: PUT/PATCH /resource/{id}/ (actualizar)
- DestroyModelMixin: DELETE /resource/{id}/ (eliminar)
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from core.users.models import User
from core.common.models import Bitacora
from .serializers import (
    UserBasicSerializer, UserDetailSerializer, UserRegistrationSerializer,
    AdminUserRegistrationSerializer, LoginSerializer, UserSearchSerializer,
    UserStatsSerializer
)


class UserRegistrationView(CreateAPIView):
    """
    📝 MICROCONCEPTO: CreateAPIView
    
    CreateAPIView es una vista genérica que:
    - Solo maneja POST requests
    - Usa CreateModelMixin automáticamente
    - Ideal para endpoints de registro, creación, etc.
    - Permite personalizar el proceso de creación
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Público
    
    def perform_create(self, serializer):
        """
        📝 MICROCONCEPTO: perform_create()
        
        perform_create() se ejecuta después de la validación
        pero antes de guardar. Útil para:
        - Agregar datos adicionales
        - Logging
        - Envío de emails
        - Lógica de negocio post-validación
        """
        user = serializer.save()
        
        # Registrar en bitácora
        Bitacora.objects.create(
            accion=f"Nuevo usuario registrado: {user.username}",
            ip=self.get_client_ip(),
            usuario=user
        )
        
    def get_client_ip(self):
        """Obtener IP del cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class AdminUserRegistrationView(CreateAPIView):
    """
    Vista para que administradores registren usuarios con roles específicos
    """
    
    serializer_class = AdminUserRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        📝 MICROCONCEPTO: Permisos dinámicos
        
        get_permissions() permite definir permisos dinámicamente
        basados en el request, usuario, etc.
        """
        permission_classes = [permissions.IsAuthenticated]
        
        # Solo administradores pueden usar este endpoint
        if self.request.user.is_authenticated:
            if not self.request.user.groups.filter(name='administrador').exists():
                permission_classes = [permissions.IsAdminUser]  # Esto denegará acceso
                
        return [permission() for permission in permission_classes]
        
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Registrar en bitácora
        Bitacora.objects.create(
            accion=f"Usuario creado por administrador: {user.username} con rol {serializer.validated_data.get('rol')}",
            ip=self.get_client_ip(),
            usuario=self.request.user
        )
        
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class LoginView(APIView):
    """
    📝 MICROCONCEPTO: APIView personalizada
    
    APIView es la clase base más flexible. Útil cuando:
    - Necesitamos lógica muy específica
    - No encaja en patrones estándar de CRUD
    - Queremos control total sobre el request/response
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        📝 MICROCONCEPTO: Métodos HTTP personalizados
        
        En APIView definimos métodos para cada verbo HTTP:
        - get(), post(), put(), patch(), delete()
        """
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Actualizar last_login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Registrar en bitácora
            Bitacora.objects.create(
                accion="Login exitoso",
                ip=self.get_client_ip(request),
                usuario=user
            )
            
            # Obtener permisos del usuario
            permissions_list = []
            for group in user.groups.all():
                permissions_list.extend(
                    group.permissions.values_list('codename', flat=True)
                )
            
            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'groups': list(user.groups.values_list('name', flat=True)),
                    'permissions': list(set(permissions_list))
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserViewSet(viewsets.ModelViewSet):
    """
    📝 MICROCONCEPTO: ModelViewSet completo
    
    ModelViewSet proporciona automáticamente:
    - list(): GET /users/ (listar usuarios)
    - create(): POST /users/ (crear usuario)
    - retrieve(): GET /users/{id}/ (detalle de usuario)
    - update(): PUT /users/{id}/ (actualizar completo)
    - partial_update(): PATCH /users/{id}/ (actualizar parcial)
    - destroy(): DELETE /users/{id}/ (eliminar)
    
    Además podemos agregar acciones personalizadas con @action
    """
    
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'username']
    
    def get_serializer_class(self):
        """
        📝 MICROCONCEPTO: Serializers dinámicos
        
        get_serializer_class() permite usar diferentes serializers
        basados en la acción que se está ejecutando.
        """
        if self.action == 'list':
            return UserBasicSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return UserBasicSerializer
    
    def get_permissions(self):
        """Permisos específicos por acción"""
        if self.action == 'profile':
            # El perfil lo puede ver el propio usuario
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            # Ver usuarios requiere ser supervisor o administrador
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Crear, actualizar, eliminar solo administradores
            permission_classes = [permissions.IsAdminUser]
            
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """
        📝 MICROCONCEPTO: Acciones personalizadas con @action
        
        @action permite agregar endpoints personalizados:
        - detail=False: /users/profile/ (no requiere ID)
        - detail=True: /users/{id}/profile/ (requiere ID)
        - methods: Lista de métodos HTTP permitidos
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
            
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = UserDetailSerializer(
                user, 
                data=request.data, 
                partial=partial,
                context={'request': request}
            )
            
            if serializer.is_valid():
                # Solo administradores pueden cambiar is_active
                if 'is_active' in serializer.validated_data:
                    if not request.user.groups.filter(name='administrador').exists():
                        serializer.validated_data.pop('is_active')
                
                serializer.save()
                
                # Registrar en bitácora
                Bitacora.objects.create(
                    accion=f"Perfil actualizado: {user.username}",
                    ip=self.get_client_ip(request),
                    usuario=user
                )
                
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        📝 MICROCONCEPTO: Búsqueda personalizada
        
        Implementamos búsqueda más específica que el filtro automático.
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'results': []})
        
        # Búsqueda en username y email
        users = User.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).select_related().prefetch_related('groups')[:10]  # Limitar resultados
        
        serializer = UserSearchSerializer(users, many=True)
        return Response({
            'count': len(users),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Listar solo usuarios activos"""
        active_users = self.queryset.filter(is_active=True)
        
        # Aplicar paginación
        page = self.paginate_queryset(active_users)
        if page is not None:
            serializer = UserBasicSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserBasicSerializer(active_users, many=True)
        return Response({
            'count': active_users.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='by-role/(?P<role_name>[^/.]+)')
    def by_role(self, request, role_name=None):
        """
        📝 MICROCONCEPTO: URLs con parámetros personalizados
        
        url_path permite definir URLs más complejas con parámetros.
        """
        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response(
                {'error': f'Rol "{role_name}" no encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        users = User.objects.filter(groups=group).select_related()
        
        # Obtener información del rol extendido si existe
        rol_extendido = getattr(group, 'rol_extendido', None)
        
        return Response({
            'rol': {
                'nombre': group.name,
                'descripcion': rol_extendido.descripcion if rol_extendido else '',
                'total_usuarios': users.count()
            },
            'usuarios': UserBasicSerializer(users, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        📝 MICROCONCEPTO: Endpoints de estadísticas
        
        Útil para dashboards y reportes.
        """
        total_usuarios = User.objects.count()
        usuarios_activos = User.objects.filter(is_active=True).count()
        
        # Usuarios por rol
        usuarios_por_rol = {}
        for group in Group.objects.all():
            count = User.objects.filter(groups=group).count()
            if count > 0:
                usuarios_por_rol[group.name] = count
        
        # Registros del último mes
        ultimo_mes = timezone.now() - timedelta(days=30)
        registros_ultimo_mes = User.objects.filter(date_joined__gte=ultimo_mes).count()
        
        # Último login
        ultimo_login_user = User.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login').first()
        
        # Usuarios nuevos hoy
        hoy = timezone.now().date()
        usuarios_nuevos_hoy = User.objects.filter(date_joined__date=hoy).count()
        
        stats_data = {
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_por_rol': usuarios_por_rol,
            'registros_ultimo_mes': registros_ultimo_mes,
            'ultimo_login': ultimo_login_user.last_login if ultimo_login_user else None,
            'usuarios_nuevos_hoy': usuarios_nuevos_hoy,
            'usuarios_inactivos': total_usuarios - usuarios_activos
        }
        
        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip