# users/views.py
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from datetime import timedelta

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserBasicSerializer, UserDetailSerializer, UserRegistrationSerializer,
    AdminUserRegistrationSerializer, LoginSerializer, UserSearchSerializer,
    UserStatsSerializer
)

User = get_user_model()

# Bitacora: si no existe el modelo Bitacora, evitamos excepción (mejor importarlo correctamente)
try:
    from core.bitacora.models import Bitacora
except Exception:
    Bitacora = None


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if Bitacora:
            Bitacora.objects.create(
                accion=f"Nuevo usuario registrado: {user.username}",
                ip=self.get_client_ip(),
                usuario=user
            )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')

class AdminUserRegistrationView(CreateAPIView):
    serializer_class = AdminUserRegistrationSerializer
    permission_classes = [permissions.IsAdminUser]  # Recomendado para producción

    def perform_create(self, serializer):
        user = serializer.save()
        if Bitacora:
            Bitacora.objects.create(
                accion=f"Usuario creado por administrador: {user.username}",
                ip=self.get_client_ip(),
                usuario=self.request.user if self.request.user.is_authenticated else None
            )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')

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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'username']

    def get_serializer_class(self):
        if self.action == 'list':
            return UserBasicSerializer
        elif self.action in ['retrieve', 'update', 'partial_update', 'profile']:
            return UserDetailSerializer
        return UserBasicSerializer

    def get_permissions(self):
        if self.action == 'profile':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
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
                    accion=f"Perfil actualizado: {user.username}",
                    ip=self.get_client_ip(request),
                    usuario=user
                )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '')
        if not q:
            return Response({'count': 0, 'results': []})
        users = User.objects.filter(Q(username__icontains=q) | Q(email__icontains=q)).prefetch_related('groups')[:10]
        serializer = UserSearchSerializer(users, many=True)
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
            return Response({'error': f'Rol "{role_name}" no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        users = User.objects.filter(groups=group)
        return Response({
            'rol': {'nombre': group.name, 'total_usuarios': users.count()},
            'usuarios': UserBasicSerializer(users, many=True).data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_usuarios = User.objects.count()
        usuarios_activos = User.objects.filter(is_active=True).count()
        usuarios_por_rol = {g.name: User.objects.filter(groups=g).count() for g in Group.objects.all() if User.objects.filter(groups=g).exists()}
        ultimo_mes = timezone.now() - timedelta(days=30)
        registros_ultimo_mes = User.objects.filter(date_joined__gte=ultimo_mes).count()
        ultimo_login_user = User.objects.filter(last_login__isnull=False).order_by('-last_login').first()
        hoy = timezone.now().date()
        usuarios_nuevos_hoy = User.objects.filter(date_joined__date=hoy).count()

        stats_data = {
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_por_rol': usuarios_por_rol,
            'registros_ultimo_mes': registros_ultimo_mes,
            'ultimo_login': (ultimo_login_user.last_login if ultimo_login_user else None),
            'usuarios_nuevos_hoy': usuarios_nuevos_hoy,
            'usuarios_inactivos': total_usuarios - usuarios_activos
        }

        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
