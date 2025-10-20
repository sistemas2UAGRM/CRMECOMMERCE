# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile, Direccion

User = get_user_model()  # Respetamos AUTH_USER_MODEL

# Serializers básicos / detallados
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'full_name', 'is_active', 'date_joined']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['foto_perfil', 'preferencias_ui']

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'
        read_only_fields = ['user'] # El usuario se asignará automáticamente

class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    rol_actual = serializers.SerializerMethodField()
    puede_editar_estado = serializers.SerializerMethodField()
    profile = UserProfileSerializer()
    direcciones = DireccionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'full_name', 'fecha_de_nacimiento', 'sexo', 'celular',
                  'is_active', 'date_joined', 'last_login', 'rol_actual',
                  'puede_editar_estado', 'profile', 'direcciones'] 
        read_only_fields = ['id', 'date_joined', 'last_login', 'direcciones']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_rol_actual(self, obj):
        grupo = obj.groups.first()
        if grupo:
            return {'nombre': grupo.name}
        return None

    def get_puede_editar_estado(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return request.user.groups.filter(name='administrador').exists()
        return False

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        instance = super().update(instance, validated_data)

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    acepta_terminos = serializers.BooleanField(write_only=True)
    acepta_marketing = serializers.BooleanField(default=False, write_only=True)

    verification_email_sent = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)
    rol_asignado = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'fecha_de_nacimiento', 'sexo',
                  'celular', 'acepta_terminos', 'acepta_marketing',
                  'verification_email_sent', 'message', 'rol_asignado',
                  'is_active', 'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_acepta_terminos(self, value):
        if not value:
            raise serializers.ValidationError("Debe aceptar los términos y condiciones.")
        return value

    def validate(self, data):
        pw = data.get('password')
        pw_conf = data.get('password_confirm')
        if not pw or not pw_conf:
            raise serializers.ValidationError({'password': 'Contraseña y confirmación son requeridas.'})
        if pw != pw_conf:
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden.'})
        return data

    def create(self, validated_data):
        # Popear campos no-modelo
        validated_data.pop('password_confirm', None)
        validated_data.pop('acepta_terminos', None)
        acepta_marketing = validated_data.pop('acepta_marketing', False)
        password = validated_data.pop('password')

        # Crear usuario usando create_user para hashear la contraseña correctamente.
        user = User.objects.create_user(password=password, **validated_data)

        # Asignar rol por defecto 'cliente'
        cliente_group, _ = Group.objects.get_or_create(name='cliente')
        user.groups.add(cliente_group)

        # Aquí podrías disparar envío de email en una tarea asíncrona (celery, rq) o directamente
        # send_verification_email(user)

        return user

    def get_rol_asignado(self, obj):
        grupo = obj.groups.first()
        if grupo:
            return {'id': grupo.id, 'nombre': grupo.name}
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['verification_email_sent'] = True
        data['message'] = "Registro exitoso. Revisa tu email para verificar tu cuenta."
        return data


class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    rol = serializers.ChoiceField(choices=['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente'],
                                  write_only=True)
    send_welcome_email = serializers.BooleanField(default=True, write_only=True)

    password_temporal = serializers.BooleanField(read_only=True)
    debe_cambiar_password = serializers.BooleanField(read_only=True)
    rol_asignado = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name',
                  'last_name', 'fecha_de_nacimiento', 'sexo', 'celular',
                  'rol', 'send_welcome_email', 'password_temporal',
                  'debe_cambiar_password', 'rol_asignado', 'is_active',
                  'date_joined']
        read_only_fields = ['id', 'is_active', 'date_joined']

    def validate_rol(self, value):
        valid_roles = ['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Rol debe ser uno de: {valid_roles}")
        return value

    def create(self, validated_data):
        rol = validated_data.pop('rol')
        send_welcome_email = validated_data.pop('send_welcome_email', True)
        password = validated_data.pop('password', None)

        if not password:
            password = User.objects.make_random_password(length=12)

        user = User.objects.create_user(password=password, **validated_data)

        group, _ = Group.objects.get_or_create(name=rol)
        user.groups.add(group)

        if rol == 'administrador':
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            # Asignar todos los permisos al grupo administrador (si se desea)
            all_permissions = Permission.objects.all()
            group.permissions.set(all_permissions)

        elif rol == 'empleadonivel1':
            user.is_staff = True
            user.save()

        # Marcar respuestas read-only
        return user

    def get_rol_asignado(self, obj):
        grupo = obj.groups.first() if not isinstance(obj, dict) else None
        if grupo:
            descriptions = {
                'administrador': 'Administrador con acceso total al sistema',
                'empleadonivel1': 'Supervisor con permisos de gestión',
                'empleadonivel2': 'Vendedor con permisos de venta',
                'cliente': 'Cliente con acceso básico'
            }
            return {'id': grupo.id, 'nombre': grupo.name, 'descripcion': descriptions.get(grupo.name, '')}
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['password_temporal'] = True
        data['debe_cambiar_password'] = True
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise serializers.ValidationError('Debe incluir email y contraseña.', code='authorization')

        # authenticate() uses configured AUTHENTICATION_BACKENDS
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise serializers.ValidationError('Credenciales inválidas.', code='authorization')
        if not user.is_active:
            raise serializers.ValidationError('Cuenta desactivada.', code='authorization')

        data['user'] = user
        return data


class UserSearchSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'rol']

    def get_rol(self, obj):
        grupo = obj.groups.first()
        return grupo.name if grupo else None


class UserStatsSerializer(serializers.Serializer):
    total_usuarios = serializers.IntegerField()
    usuarios_activos = serializers.IntegerField()
    usuarios_por_rol = serializers.DictField()
    registros_ultimo_mes = serializers.IntegerField()
    ultimo_login = serializers.DateTimeField(allow_null=True)
    usuarios_nuevos_hoy = serializers.IntegerField()
    usuarios_inactivos = serializers.IntegerField()
