# apps/users/serializers.py
"""
Serializers para la app `users`.

Contienen:
- Serializers para listar/mostrar/editar usuarios.
- Serializers para registro público y creación por admin.
- Serializers para perfil y direcciones.
Cada clase incluye docstrings y comentarios para facilitar su mantenimiento.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile, Direccion

User = get_user_model()


# -----------------------
# Serializers públicos / básicos
# -----------------------
class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer compacto para listas de usuarios (p. ej. tablas, búsquedas).
    Incluye nombre completo calculado.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        # Campos mínimos a exponer en listados públicos/administrativos
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'is_active', 'is_staff', 'date_joined']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para datos del perfil relacionados (OneToOne).
    Solo expone los campos que necesitamos en los endpoints de usuario.
    """
    class Meta:
        model = UserProfile
        fields = ['foto_perfil', 'razon_social', 'tipo_documento_fiscal', 'numero_documento_fiscal', 'preferencias_ui']


class DireccionSerializer(serializers.ModelSerializer):
    """
    Serializer para Direccion.
    - 'user' se marca read_only: el usuario debe asignarse desde la vista (request.user)
      o mediante el contexto del serializer.
    - Al crear/actualizar no manejamos la lógica de 'es_predeterminada' aquí porque
      está encapsulada en el modelo (save override).
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Direccion
        fields = '__all__'
        read_only_fields = ['user', 'id']

    def create(self, validated_data):
        """
        Asigna el user desde el contexto (request.user) si está disponible.
        Esto evita permitir al cliente enviar otro user_id en el payload.
        """
        request = self.context.get('request', None)
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        if not user:
            raise serializers.ValidationError("Usuario no autenticado: no se puede crear dirección.")
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Evitar cambiar el user por payload malicioso.
        """
        validated_data.pop('user', None)
        return super().update(instance, validated_data)


# -----------------------
# Serializers detallados / lectura y actualización
# -----------------------
class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para un solo usuario (perfil completo).
    Permite:
    - lectura de profile (anidado)
    - lectura de direcciones (solo lectura)
    - actualización parcial de campos básicos + perfil.
    La actualización del perfil se hace dentro del método update.
    """
    full_name = serializers.SerializerMethodField()
    current_role = serializers.SerializerMethodField(read_only=True)
    can_edit_status = serializers.SerializerMethodField()
    profile = UserProfileSerializer(required=False)
    direcciones = DireccionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'fecha_de_nacimiento', 'sexo', 'celular',
            'is_active', 'date_joined', 'last_login', 'current_role',
            'can_edit_status', 'profile', 'direcciones'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'direcciones', 'email']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_current_role(self, obj):
        """
        Devuelve el primer grupo (rol) del usuario en formato simple.
        Si necesitas múltiples roles, cambia la lógica para devolver una lista.
        """
        grupo = obj.groups.first()
        if grupo:
            return {'id': grupo.id, 'name': grupo.name}
        return None

    def get_can_edit_status(self, obj):
        """
        Indica si el usuario que hace la petición puede editar el estado (is_active).
        Aquí se define que sólo miembros del grupo 'administrador' pueden hacerlo.
        """
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return request.user.groups.filter(name='administrador').exists()
        return False

    def update(self, instance, validated_data):
        """
        Actualiza campos del usuario y del perfil anidado.
        - Protege el email de cambios directos (read_only en Meta).
        - Si el perfil no existe, lo crea.
        """
        profile_data = validated_data.pop('profile', None)

        # Actualizar campos del user (excluye email por seguridad)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar o crear profile
        if profile_data is not None:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


# -----------------------
# Serializers de autenticación / registro
# -----------------------
class UserSignupSerializer(serializers.ModelSerializer):
    """
    Serializer para registro público de usuarios (signup).
    - Valida contraseñas (usando validators de Django).
    - Crea usuario usando el manager (create_user) para respetar lógica central.
    - No activa al usuario por defecto (gestiona verificación por email).
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    acepta_terminos = serializers.BooleanField(write_only=True)
    acepta_marketing = serializers.BooleanField(default=False, write_only=True)

    # Campos de respuesta amigables
    verification_email_sent = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)
    assigned_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'fecha_de_nacimiento', 'sexo',
            'celular', 'acepta_terminos', 'acepta_marketing',
            'verification_email_sent', 'message', 'assigned_role',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'is_active', 'date_joined']

    def validate_password(self, value):
        """
        Valida la contraseña según las reglas configuradas en Django.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        """
        Evita registros duplicados por email.
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate_acepta_terminos(self, value):
        if not value:
            raise serializers.ValidationError("Debe aceptar los términos y condiciones.")
        return value

    def validate(self, data):
        """
        Validación cruzada entre password y password_confirm.
        """
        pw = data.get('password')
        pw_conf = data.get('password_confirm')
        if not pw or not pw_conf:
            raise serializers.ValidationError({'password': 'Contraseña y confirmación son requeridas.'})
        if pw != pw_conf:
            raise serializers.ValidationError({'password_confirm': 'Las contraseñas no coinciden.'})
        return data

    def create(self, validated_data):
        """
        Crea el usuario:
        - Extrae campos no-modelo.
        - Usa el manager `create_user` para respetar reglas (is_active=False por defecto).
        - Asigna el grupo 'cliente'.
        - No se envía email aquí (dejar a tarea asíncrona desde la vista/servicio).
        """
        validated_data.pop('password_confirm', None)
        validated_data.pop('acepta_terminos', None)
        acepta_marketing = validated_data.pop('acepta_marketing', False)
        password = validated_data.pop('password')

        # Extraer email y username (requeridos por create_user en tu manager)
        email = validated_data.pop('email')
        username = validated_data.pop('username')

        # Create user via manager to centralize behavior
        user = User.objects.create_user(email=email, username=username, password=password, **validated_data)
        # Guardar preferencia de marketing en profile (si aplica)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.preferencias_ui = profile.preferencias_ui or {}
        profile.save()
        # Guardar flag de marketing directamente en user (si lo tienes en el modelo)
        if hasattr(user, 'acepta_marketing'):
            user.acepta_marketing = acepta_marketing
            user.save(update_fields=['acepta_marketing'])

        # Asignar rol por defecto 'cliente'
        cliente_group, _ = Group.objects.get_or_create(name='cliente')
        user.groups.add(cliente_group)

        # Nota: En la vista deberías disparar una tarea para enviar el email de verificación

        return user

    def get_assigned_role(self, obj):
        grupo = obj.groups.first()
        if grupo:
            return {'id': grupo.id, 'name': grupo.name}
        return None

    def to_representation(self, instance):
        """
        Representación personalizada para la respuesta de registro.
        Indica al cliente que revise su email.
        """
        data = super().to_representation(instance)
        data['verification_email_sent'] = True
        data['message'] = "Registro exitoso. Revisa tu email para verificar tu cuenta."
        return data


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer que usan los administradores para crear usuarios desde el panel/admin API.
    - Se puede generar password temporal si no se suministra.
    - Permite asignar roles predefinidos.
    - Ajusta flags como is_staff/is_superuser según el rol.
    """
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.ChoiceField(choices=['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente'],
                                   write_only=True)
    send_welcome_email = serializers.BooleanField(default=True, write_only=True)

    # Campos de respuesta
    temporary_password = serializers.BooleanField(read_only=True)
    must_change_password = serializers.BooleanField(read_only=True)
    assigned_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'first_name',
            'last_name', 'fecha_de_nacimiento', 'sexo', 'celular',
            'role', 'send_welcome_email', 'temporary_password',
            'must_change_password', 'assigned_role', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'is_active', 'date_joined']

    def validate_role(self, value):
        valid_roles = ['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Rol debe ser uno de: {valid_roles}")
        return value

    def create(self, validated_data):
        """
        Crear usuario con rol administrativo desde backend:
        - Se genera password aleatorio si no se proporciona.
        - Se asigna el grupo correspondiente y permisos básicos si aplica.
        """
        role = validated_data.pop('role')
        send_welcome_email = validated_data.pop('send_welcome_email', True)
        password = validated_data.pop('password', None)

        if not password:
            password = User.objects.make_random_password(length=12)
            temporary = True
        else:
            temporary = False

        email = validated_data.pop('email')
        username = validated_data.pop('username')

        # Crear usuario (create_user aplica las reglas del manager)
        user = User.objects.create_user(email=email, username=username, password=password, **validated_data)

        # Asignar grupo/role
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        # Ajustes por role
        if role == 'administrador':
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save(update_fields=['is_staff', 'is_superuser', 'is_active'])
            # Si se desea otorgar todos los permisos al grupo admin:
            all_permissions = Permission.objects.all()
            group.permissions.set(all_permissions)

        elif role == 'empleado':
            user.is_staff = True
            user.is_active = True
            user.save(update_fields=['is_staff'])

        # Nota: enviar email de bienvenida desde la vista o una tarea asíncrona si send_welcome_email True

        return user

    def get_assigned_role(self, obj):
        grupo = obj.groups.first()
        if grupo:
            descriptions = {
                'administrador': 'Administrador con acceso total al sistema',
                'empleadonivel1': 'Supervisor con permisos de gestión',
                'empleadonivel2': 'Vendedor con permisos de venta',
                'cliente': 'Cliente con acceso básico'
            }
            return {'id': grupo.id, 'name': grupo.name, 'description': descriptions.get(grupo.name, '')}
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['temporary_password'] = True  # si quieres indicar al cliente que la contraseña es temporal
        data['must_change_password'] = True
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login clásico por email + password.
    Devuelve el user en validated_data si las credenciales son correctas.
    El manejo de tokens (JWT/session) lo hace la vista.
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise serializers.ValidationError('Debe incluir email y contraseña.', code='authorization')

        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise serializers.ValidationError('Credenciales inválidas.', code='authorization')
        if not user.is_active:
            raise serializers.ValidationError('Cuenta desactivada.', code='authorization')
        if not user.is_verified:
            raise serializers.ValidationError(
                'Esta cuenta no ha sido verificada. Revisa tu email.', 
                code='authorization'
            )
        
        data['user'] = user
        return data


# -----------------------
# Serializers para listados/búsquedas avanzadas y estadísticas
# -----------------------
class UserAdminListSerializer(serializers.ModelSerializer):
    """
    Serializer para listados administrativos con rol incluido.
    (Se puede usar para búsquedas o selectores en el admin UI)
    """
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 
                  'last_name', 'is_active', 'is_staff', 'role', 'fecha_de_nacimiento',
                  'sexo', 'celular', 'is_verified'
        ]

    def get_role(self, obj):
        grupo = obj.groups.first()
        return grupo.name if grupo else None


class UserStatisticsSerializer(serializers.Serializer):
    """
    Serializer para devolver estadísticas agregadas sobre usuarios.
    Debes poblar los campos desde la vista con los cálculos necesarios.
    Campos esperados:
    - total_users (int)
    - active_users (int)
    - users_by_role (dict)
    - registered_last_month (int)
    - last_login (datetime or null)
    - new_users_today (int)
    - inactive_users (int)
    """
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    users_by_role = serializers.DictField(child=serializers.IntegerField())
    registered_last_month = serializers.IntegerField()
    last_login = serializers.DateTimeField(allow_null=True)
    new_users_today = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
