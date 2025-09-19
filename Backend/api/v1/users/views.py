# api/v1/users/views.py

"""
MICROCONCEPTOS - DJANGO REST FRAMEWORK VIEWS

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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.users.models import User
from core.common.models import Bitacora
from .serializers import (
    UserBasicSerializer, UserDetailSerializer, UserRegistrationSerializer,
    AdminUserRegistrationSerializer, LoginSerializer, UserSearchSerializer,
    UserStatsSerializer
)


class UserRegistrationView(CreateAPIView):
    """
    MICROCONCEPTO: CreateAPIView
    
    CreateAPIView es una vista genérica que:
    - Solo maneja POST requests
    - Usa CreateModelMixin automáticamente
    - Ideal para endpoints de registro, creación, etc.
    - Permite personalizar el proceso de creación
    """
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Público
    
    @swagger_auto_schema(
        operation_description="Registro público de clientes",
        request_body=UserRegistrationSerializer,
        security=[],  # Endpoint público - sin autenticación
        responses={
            201: openapi.Response(
                description='Usuario registrado exitosamente',
                schema=UserBasicSerializer,
                examples={
                    'application/json': {
                        'id': 5,
                        'username': 'juan.cliente',
                        'email': 'juan@gmail.com',
                        'first_name': 'Juan',
                        'last_name': 'Pérez',
                        'full_name': 'Juan Pérez',
                        'is_active': True,
                        'date_joined': '2024-09-19T01:00:00Z'
                    }
                }
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'username': ['Este campo es requerido.'],
                        'email': ['Ingrese una dirección de email válida.'],
                        'password': ['La contraseña es muy común.']
                    }
                }
            )
        },
        tags=['Autenticación']
    )
    def perform_create(self, serializer):
        """
        MICROCONCEPTO: perform_create()
        
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
    TEMPORAL: Sin protección para configuración inicial
    """
    
    serializer_class = AdminUserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # TEMPORAL: Sin protección
    
    @swagger_auto_schema(
        operation_description="Registro de usuarios por administrador con roles específicos",
        request_body=AdminUserRegistrationSerializer,
        security=[],  # TEMPORAL: Endpoint público para configuración inicial
        responses={
            201: openapi.Response(
                description='Usuario creado exitosamente por administrador',
                schema=UserDetailSerializer,
                examples={
                    'application/json': {
                        'id': 3,
                        'username': 'supervisor.ventas',
                        'email': 'supervisor@empresa.com',
                        'first_name': 'María',
                        'last_name': 'González',
                        'full_name': 'María González',
                        'is_active': True,
                        'groups': [
                            {
                                'id': 2,
                                'name': 'empleadonivel1'
                            }
                        ],
                        'date_joined': '2024-09-19T01:00:00Z',
                        'last_login': None
                    }
                }
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'rol': ['Rol inválido. Opciones: administrador, empleadonivel1, empleadonivel2, cliente'],
                        'username': ['Ya existe un usuario con este nombre.']
                    }
                }
            )
        },
        tags=['Administración']
    )
    def perform_create(self, serializer):
        user = serializer.save()
        
        # Registrar en bitácora
        Bitacora.objects.create(
            accion=f"Usuario creado por administrador: {user.username} con rol {serializer.validated_data.get('rol')}",
            ip=self.get_client_ip(),
            usuario=self.request.user if self.request.user.is_authenticated else None
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
    MICROCONCEPTO: APIView personalizada
    
    APIView es la clase base más flexible. Útil cuando:
    - Necesitamos lógica muy específica
    - No encaja en patrones estándar de CRUD
    - Queremos control total sobre el request/response
    """
    
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Autenticación de usuario con JWT",
        request_body=LoginSerializer,
        security=[],  # Endpoint público - sin autenticación
        responses={
            200: openapi.Response(
                description='Autenticación exitosa',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access_token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de acceso JWT'),
                        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de renovación JWT'),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'groups': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                                'permissions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                            }
                        )
                    }
                ),
                examples={
                    'application/json': {
                        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'user': {
                            'id': 1,
                            'username': 'admin',
                            'email': 'admin@empresa.com',
                            'first_name': 'Administrador',
                            'last_name': 'Sistema',
                            'groups': ['administrador'],
                            'permissions': ['add_user', 'change_user', 'delete_user']
                        }
                    }
                }
            ),
            400: openapi.Response(
                description='Error de autenticación',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                ),
                examples={
                    'application/json': {
                        'error': 'Credenciales inválidas'
                    }
                }
            )
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        MICROCONCEPTO: Métodos HTTP personalizados
        
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
    MICROCONCEPTO: ModelViewSet completo
    
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
    
    @swagger_auto_schema(
        operation_description="Listar todos los usuarios del sistema",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description='Lista de usuarios',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                        }
                    )
                ),
                examples={
                    'application/json': [
                        {
                            'id': 1,
                            'username': 'admin',
                            'email': 'admin@empresa.com',
                            'first_name': 'Admin',
                            'last_name': 'Sistema',
                            'full_name': 'Admin Sistema',
                            'is_active': True,
                            'date_joined': '2024-09-19T01:00:00Z'
                        }
                    ]
                }
            ),
            401: openapi.Response(
                description='No autorizado',
                examples={
                    'application/json': {
                        'detail': 'Authentication credentials were not provided.'
                    }
                }
            )
        },
        tags=['Usuarios - Administración']
    )
    def list(self, request, *args, **kwargs):
        """Lista todos los usuarios - Solo administradores y supervisores"""
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """
        MICROCONCEPTO: Serializers dinámicos
        
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
    
    @swagger_auto_schema(
        methods=['get'],
        operation_description="Obtener perfil del usuario actual",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description='Perfil del usuario',
                schema=UserDetailSerializer
            )
        },
        tags=['Usuarios']
    )
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Actualizar perfil del usuario actual",
        security=[{'Bearer': []}],
        request_body=UserDetailSerializer,
        responses={
            200: openapi.Response(
                description='Perfil actualizado exitosamente',
                schema=UserDetailSerializer
            ),
            400: openapi.Response(
                description='Error de validación',
                examples={
                    'application/json': {
                        'email': ['Ingrese una dirección de email válida.'],
                        'first_name': ['Este campo no puede estar en blanco.']
                    }
                }
            )
        },
        tags=['Usuarios']
    )
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        """
        MICROCONCEPTO: Acciones personalizadas con @action
        
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
    
    @swagger_auto_schema(
        operation_description="Buscar usuarios por nombre de usuario o email",
        manual_parameters=[
            openapi.Parameter(
                'q',
                openapi.IN_QUERY,
                description='Término de búsqueda',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Resultados de búsqueda',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'groups': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
                                }
                            )
                        )
                    }
                ),
                examples={
                    'application/json': {
                        'count': 2,
                        'results': [
                            {
                                'id': 1,
                                'username': 'juan.cliente',
                                'email': 'juan@gmail.com',
                                'full_name': 'Juan Pérez',
                                'is_active': True,
                                'groups': ['cliente']
                            },
                            {
                                'id': 2,
                                'username': 'maria.supervisor',
                                'email': 'maria@empresa.com',
                                'full_name': 'María González',
                                'is_active': True,
                                'groups': ['empleadonivel1']
                            }
                        ]
                    }
                }
            )
        },
        tags=['Usuarios']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        MICROCONCEPTO: Búsqueda personalizada
        
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
    
    @swagger_auto_schema(
        operation_description="Listar solo usuarios activos",
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description='Lista de usuarios activos',
                schema=UserBasicSerializer(many=True)
            )
        },
        tags=['Usuarios - Consultas']
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Listar solo usuarios activos"""
        queryset = self.queryset.filter(is_active=True)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Obtener usuarios por rol específico",
        security=[{'Bearer': []}],
        manual_parameters=[
            openapi.Parameter(
                'role_name',
                openapi.IN_PATH,
                description='Nombre del rol',
                type=openapi.TYPE_STRING,
                enum=['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente'],
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description='Usuarios con el rol especificado',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'rol': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nombre': openapi.Schema(type=openapi.TYPE_STRING),
                                'descripcion': openapi.Schema(type=openapi.TYPE_STRING),
                                'total_usuarios': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'usuarios': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'username': openapi.Schema(type=openapi.TYPE_STRING),
                                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                                    'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                    'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                                }
                            )
                        )
                    }
                ),
                examples={
                    'application/json': {
                        'rol': {
                            'nombre': 'administrador',
                            'descripcion': 'Administrador con acceso total al sistema',
                            'total_usuarios': 2
                        },
                        'usuarios': [
                            {
                                'id': 1,
                                'username': 'admin',
                                'email': 'admin@empresa.com',
                                'first_name': 'Admin',
                                'last_name': 'Sistema',
                                'full_name': 'Admin Sistema',
                                'is_active': True,
                                'date_joined': '2024-09-19T01:00:00Z'
                            }
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description='Rol no encontrado',
                examples={
                    'application/json': {
                        'error': 'Rol "vendedor_inexistente" no encontrado'
                    }
                }
            )
        },
        tags=['Usuarios - Consultas']
    )
    @action(detail=False, methods=['get'], url_path='by-role/(?P<role_name>[^/.]+)')
    def by_role(self, request, role_name=None):
        """
        MICROCONCEPTO: URLs con parámetros personalizados
        
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
    
    @swagger_auto_schema(
        operation_description="Obtener estadísticas del sistema de usuarios",
        responses={
            200: openapi.Response(
                description='Estadísticas del sistema',
                schema=UserStatsSerializer,
                examples={
                    'application/json': {
                        'total_usuarios': 25,
                        'usuarios_activos': 23,
                        'usuarios_inactivos': 2,
                        'usuarios_por_rol': {
                            'administrador': 2,
                            'empleadonivel1': 5,
                            'empleadonivel2': 8,
                            'cliente': 10
                        },
                        'registros_ultimo_mes': 8,
                        'usuarios_nuevos_hoy': 2,
                        'ultimo_login': '2024-09-19T01:30:00Z'
                    }
                }
            ),
            403: openapi.Response(
                description='Sin permisos para ver estadísticas',
                examples={
                    'application/json': {
                        'detail': 'No tiene permisos para realizar esta acción.'
                    }
                }
            )
        },
        tags=['Usuarios - Administración']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        MICROCONCEPTO: Endpoints de estadísticas
        
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