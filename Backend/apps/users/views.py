# backend/apps/users/views.py
"""
Views (DRF) para la app users:
- Registro público (dispara envío de email de verificación)
- Reenvío de verificación
- Verificación por token (GET)
- Login (ya existente)
- ViewSet para CRUD de usuarios (administración)
- Gestión de direcciones (ya incluida)
"""
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q, Count
from datetime import timedelta

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings as jwt_settings

from .tasks import send_verification_email_task

from .serializers import (
    UserListSerializer, UserDetailSerializer, UserSignupSerializer, 
    LoginSerializer, UserAdminListSerializer,
    UserStatisticsSerializer, DireccionSerializer, 
    AdminCreateUserSerializer
)
from .models import Direccion

User = get_user_model()

# Bitacora: si no existe el modelo Bitacora, evitamos excepción (mejor importarlo correctamente)
try:
    from bitacora.models import Bitacora
except Exception:
    Bitacora = None


class UserSignupView(CreateAPIView):
    """
    - Crea el usuario (is_active=False por defecto).
    - Lanza una tarea asíncrona para enviar el email de verificación.
    """
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if Bitacora:
            Bitacora.objects.create(
                accion=f"Nuevo usuario registrado: {user.email}",
                ip=self.get_client_ip(),
                usuario=user
            )

        # Desactivado temporalmente el envío de correos de verificación
        # try:
        #     send_verification_email_task.delay(user.id)
        # except Exception:
        #     send_verification_email_task(user.id)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
    
class VerifyEmailView(APIView):
    """
    - Marca is_verified=True e is_active=True si el token existe.
    - Rotar verification_uuid por seguridad (genera uno nuevo).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({"detail": "Token de verificación requerido."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token_uuid = uuid.UUID(token)
        except (ValueError, TypeError):
            return Response({"detail": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(verification_uuid=token_uuid)
        except User.DoesNotExist:
            return Response({"detail": "Token no encontrado o ya usado."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"detail": "Cuenta ya verificada."}, status=status.HTTP_200_OK)

        # Marcar verificada y activa
        user.is_verified = True
        user.is_active = True
        # Rotar token para impedir reuso
        user.verification_uuid = uuid.uuid4()
        user.save(update_fields=['is_verified', 'is_active', 'verification_uuid'])

        if Bitacora:
            Bitacora.objects.create(
                accion=f"Usuario verificado: {user.email}",
                ip=self._get_client_ip(),
                usuario=user
            )
        return Response({"detail": "Email verificado correctamente."}, status=status.HTTP_200_OK)

    def _get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')

class ResendVerificationView(APIView):
    """
    Payload: { "email": "user@example.com" }
    - Reenvía el email de verificación (si el usuario no está verificado).
    - Protege para no revelar existencia de emails: siempre devuelve 200 con mensaje genérico.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email requerido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # No revelar existencia: responder iguales para evitar enumeración
            return Response({"detail": "Si el email existe, recibirás un enlace de verificación."}, status=status.HTTP_200_OK)

        if user.is_verified:
            return Response({"detail": "Cuenta ya verificada."}, status=status.HTTP_200_OK)

        # Rotar token por seguridad antes de reenviar
        user.verification_uuid = uuid.uuid4()
        user.save(update_fields=['verification_uuid'])

        # Lanzar tarea asíncrona para enviar email
        try:
            send_verification_email_task.delay(user.id)
        except Exception:
            send_verification_email_task(user.id)

        return Response({"detail": "Si el email existe, recibirás un enlace de verificación."}, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            access_exp = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)

            if Bitacora:
                Bitacora.objects.create(
                    accion="Login exitoso",
                    ip=self.get_client_ip(request),
                    usuario=user
                )

            permissions_list = []
            for group in user.groups.all():
                permissions_list.extend(group.permissions.values_list('codename', flat=True))

            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'access_expires_at': access_exp.isoformat(),
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
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token requerido."}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # requiere token_blacklist app
            return Response({"detail": "Sesión cerrada."}, status=200)
        except Exception as e:
            return Response({"detail": "Token inválido o ya anulado."}, status=400)

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet administrativo para usuarios.
    - list/retrieve limitados a admin por get_permissions
    - acción 'profile' para que el usuario edite su propio perfil
    - acciones auxiliares: search, active, by_role, stats
    """
    queryset = User.objects.all().order_by('-date_joined').prefetch_related('groups')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'username']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserAdminListSerializer
        elif self.action in ['retrieve', 'update', 'partial_update', 'profile']:
            return UserDetailSerializer
        elif self.action == 'create':
            return AdminCreateUserSerializer
        return UserAdminListSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método 'create' para usar el serializer de admin.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        if Bitacora:
            ip = self._get_client_ip(request)
            Bitacora.objects.create(
                accion=f"Admin creó nuevo usuario: {user.email}",
                ip=ip,
                usuario=request.user # El admin que hizo la acción
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_permissions(self):
        if self.action == 'profile':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve', 'stats', 'by_role']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = UserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)

        partial = request.method == 'PATCH'
        serializer = UserDetailSerializer(user, data=request.data, partial=partial, context={'request': request})
        if serializer.is_valid():
            # Evitar que no-admin cambie is_active
            if 'is_active' in serializer.validated_data and not request.user.groups.filter(name='administrador').exists():
                serializer.validated_data.pop('is_active', None)

            serializer.save()
            if Bitacora:
                Bitacora.objects.create(
                    accion=f"Perfil actualizado: {user.email}",
                    ip=self._get_client_ip(request),
                    usuario=user
                )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Cambia la contraseña del usuario autenticado.
        Requiere: current_password, new_password, new_password_confirm
        """
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        # Validaciones
        if not all([current_password, new_password, new_password_confirm]):
            return Response(
                {'error': 'Todos los campos son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {'current_password': ['La contraseña actual es incorrecta']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != new_password_confirm:
            return Response(
                {'new_password_confirm': ['Las contraseñas nuevas no coinciden']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {'new_password': ['La contraseña debe tener al menos 8 caracteres']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cambiar contraseña
        user.set_password(new_password)
        user.save()

        if Bitacora:
            Bitacora.objects.create(
                accion=f"Contraseña cambiada: {user.email}",
                ip=self._get_client_ip(request),
                usuario=user
            )

        return Response(
            {'detail': 'Contraseña cambiada exitosamente'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '')
        if not q:
            return Response({'count': 0, 'results': []})
        users = User.objects.filter(Q(username__icontains=q) | Q(email__icontains=q)).prefetch_related('groups')[:10]
        serializer = UserAdminListSerializer(users, many=True)
        return Response({'count': users.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def active(self, request):
        qs = self.queryset.filter(is_active=True)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-role/(?P<role_name>[^/.]+)')
    def by_role(self, request, role_name=None):
        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return Response({'error': f'Rol \"{role_name}\" no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        users = User.objects.filter(groups=group)
        return Response({
            'rol': {'nombre': group.name, 'total_usuarios': users.count()},
            'usuarios': UserListSerializer(users, many=True).data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_usuarios = User.objects.count()
        usuarios_activos = User.objects.filter(is_active=True).count()
        roles_conteo = Group.objects.annotate(
            user_count=Count('user')
        ).filter(user_count__gt=0).values('name', 'user_count')
        
        usuarios_por_rol = {rol['name']: rol['user_count'] for rol in roles_conteo}

        ultimo_mes = timezone.now() - timedelta(days=30)
        registros_ultimo_mes = User.objects.filter(date_joined__gte=ultimo_mes).count()
        ultimo_login_user = User.objects.filter(last_login__isnull=False).order_by('-last_login').first()
        hoy = timezone.now().date()
        usuarios_nuevos_hoy = User.objects.filter(date_joined__date=hoy).count()

        stats_data = {
            'total_users': total_usuarios,
            'active_users': usuarios_activos,
            'users_by_role': usuarios_por_rol,
            'registered_last_month': registros_ultimo_mes,
            'last_login': (ultimo_login_user.last_login if ultimo_login_user else None),
            'new_users_today': usuarios_nuevos_hoy,
            'inactive_users': total_usuarios - usuarios_activos
        }

        serializer = UserStatisticsSerializer(stats_data)
        return Response(serializer.data)

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Esta vista solo debe devolver las direcciones del usuario
        actualmente autenticado.
        """
        return self.request.user.direcciones.all()

    def perform_create(self, serializer):
        """
        Asigna el usuario actual a la dirección al crearla.
        """
        serializer.save(user=self.request.user)