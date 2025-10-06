# api/v1/users/serializers.py

"""
📚 MICROCONCEPTOS - DJANGO REST FRAMEWORK SERIALIZERS

Los serializers en DRF son el puente entre los modelos de Django y las representaciones JSON.
Tienen 3 responsabilidades principales:
1. SERIALIZACIÓN: Convertir instancias de modelos a tipos de datos nativos de Python (dict, list, etc.)
2. DESERIALIZACIÓN: Convertir datos JSON/dict a instancias de modelos
3. VALIDACIÓN: Validar datos de entrada antes de crear/actualizar modelos

Tipos principales:
- Serializer: Serializer base, requiere definir todos los campos manualmente
- ModelSerializer: Automáticamente genera campos basados en el modelo
- HyperlinkedModelSerializer: Como ModelSerializer pero usa URLs en lugar de IDs para relaciones
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from core.users.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: ModelSerializer
    
    ModelSerializer es una subclase de Serializer que:
    - Automáticamente genera campos basados en el modelo
    - Incluye validadores por defecto basados en el modelo
    - Implementa métodos create() y update() por defecto
    - Reduce significativamente el código boilerplate
    
    Meta.fields controla qué campos incluir:
    - '__all__': Todos los campos del modelo
    - ['campo1', 'campo2']: Lista específica de campos
    - exclude = ['campo']: Todos excepto los excluidos
    """
    
    # Campo calculado que no existe en el modelo
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'full_name', 'is_active', 'date_joined']
        
    def get_full_name(self, obj):
        """
        📝 MICROCONCEPTO: SerializerMethodField
        
        SerializerMethodField permite crear campos calculados que no existen en el modelo.
        Debe tener un método get_<nombre_campo> que recibe la instancia del objeto.
        Es de solo lectura por defecto.
        """
        return f"{obj.first_name} {obj.last_name}".strip()


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para mostrar información completa del usuario.
    Incluye información de roles y permisos.
    """
    
    full_name = serializers.SerializerMethodField()
    rol_actual = serializers.SerializerMethodField()
    puede_editar_estado = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'full_name', 'fecha_de_nacimiento', 'sexo', 'celular',
                 'is_active', 'date_joined', 'last_login', 'rol_actual',
                 'puede_editar_estado']
        read_only_fields = ['id', 'date_joined', 'last_login']
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
        
    def get_rol_actual(self, obj):
        """Obtiene el rol principal del usuario"""
        # Asumimos que el usuario tiene un rol principal
        grupo = obj.groups.first()
        if grupo:
            return {
                'nombre': grupo.name,
                'descripcion': getattr(grupo, 'rol_extendido', {}).get('descripcion', '')
            }
        return None
        
    def get_puede_editar_estado(self, obj):
        """Solo administradores pueden editar el estado activo"""
        request = self.context.get('request')
        if request and request.user:
            return request.user.groups.filter(name='administrador').exists()
        return False


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Validación en Serializers
    
    Los serializers pueden tener varios tipos de validación:
    1. Validación de campo: validate_<campo>(self, value)
    2. Validación de objeto: validate(self, data)
    3. Validadores personalizados en el campo
    4. Validadores del modelo Django
    """
    
    password = serializers.CharField(
        write_only=True,  # No incluir en la serialización (solo para escritura)
        style={'input_type': 'password'},
        help_text="Mínimo 8 caracteres, debe incluir letras y números"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    acepta_terminos = serializers.BooleanField(write_only=True)
    acepta_marketing = serializers.BooleanField(default=False, write_only=True)
    
    # Campos de solo lectura para la respuesta
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
        """
        📝 MICROCONCEPTO: Validación de Campo Individual
        
        validate_<campo> se ejecuta para validar un campo específico.
        Debe retornar el valor validado o lanzar ValidationError.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
        
    def validate_email(self, value):
        """Validar que el email no esté en uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
        
    def validate_acepta_terminos(self, value):
        """Validar que acepta los términos"""
        if not value:
            raise serializers.ValidationError("Debe aceptar los términos y condiciones.")
        return value
        
    def validate(self, data):
        """
        📝 MICROCONCEPTO: Validación de Objeto Completo
        
        validate() se ejecuta después de todas las validaciones de campo.
        Permite validaciones que requieren múltiples campos.
        Recibe un diccionario con todos los datos validados.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return data
        
    def create(self, validated_data):
        """
        📝 MICROCONCEPTO: Método create() personalizado
        
        Sobrescribimos create() cuando necesitamos lógica personalizada
        para crear instancias. Útil para:
        - Hashear contraseñas
        - Crear objetos relacionados
        - Enviar emails
        - Logging personalizado
        """
        # Remover campos que no van al modelo
        validated_data.pop('password_confirm')
        validated_data.pop('acepta_terminos')
        acepta_marketing = validated_data.pop('acepta_marketing', False)
        
        # Crear usuario con contraseña hasheada
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Asignar rol de cliente por defecto
        cliente_group, created = Group.objects.get_or_create(name='cliente')
        user.groups.add(cliente_group)
        
        # Aquí podríamos enviar email de verificación
        # send_verification_email(user)
        
        return user
        
    def get_rol_asignado(self, obj):
        """Obtener información del rol asignado"""
        grupo = obj.groups.first()
        if grupo:
            return {
                'id': grupo.id,
                'nombre': grupo.name,
                'descripcion': 'Cliente con acceso básico'
            }
        return None
        
    def to_representation(self, instance):
        """
        📝 MICROCONCEPTO: to_representation()
        
        Personaliza cómo se serializa el objeto para la respuesta.
        Útil para:
        - Agregar campos calculados
        - Modificar formato de salida
        - Incluir datos adicionales
        """
        data = super().to_representation(instance)
        data['verification_email_sent'] = True
        data['message'] = "Registro exitoso. Revisa tu email para verificar tu cuenta."
        return data


class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de usuarios por parte del administrador.
    Permite asignar roles específicos.
    """
    
    password = serializers.CharField(write_only=True, required=False)
    rol = serializers.ChoiceField(
        choices=['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente'],
        write_only=True
    )
    send_welcome_email = serializers.BooleanField(default=True, write_only=True)
    
    # Campos de respuesta
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
        """Validar que el rol sea válido"""
        valid_roles = ['administrador', 'empleadonivel1', 'empleadonivel2', 'cliente']
        if value not in valid_roles:
            raise serializers.ValidationError(f"Rol debe ser uno de: {valid_roles}")
        return value
        
    def create(self, validated_data):
        """Crear usuario con rol específico"""
        rol = validated_data.pop('rol')
        send_welcome_email = validated_data.pop('send_welcome_email', True)
        
        # Generar contraseña temporal si no se proporciona
        password = validated_data.pop('password', None)
        if not password:
            password = User.objects.make_random_password(length=12)
            
        # Crear usuario
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Asignar rol
        group, created = Group.objects.get_or_create(name=rol)
        user.groups.add(group)
        
        # Si es administrador, asignar TODOS los permisos
        if rol == 'administrador':
            # Hacer superusuario para acceso completo
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True  # Asegurar que esté activo
            user.save()
            
            # Asignar todos los permisos disponibles
            all_permissions = Permission.objects.all()
            group.permissions.set(all_permissions)
            
            print(f"✅ Usuario administrador creado: {user.username}")
            print(f"   - is_staff: {user.is_staff}")
            print(f"   - is_superuser: {user.is_superuser}")
            print(f"   - is_active: {user.is_active}")
            
        elif rol == 'empleadonivel1':
            # Supervisor: permisos de gestión pero no de administración total
            user.is_staff = True
            user.save()
            
        # Marcar que debe cambiar contraseña
        # user.profile.debe_cambiar_password = True
        # user.profile.save()
        
        return user
        
    def get_rol_asignado(self, obj):
        """Obtener información del rol asignado"""
        # Si obj es un dict (datos validados), obtener el rol del dict
        if isinstance(obj, dict):
            rol_name = obj.get('rol')
            if rol_name:
                from django.contrib.auth.models import Group
                try:
                    grupo = Group.objects.get(name=rol_name)
                except Group.DoesNotExist:
                    return None
            else:
                return None
        else:
            # Si obj es una instancia del modelo User
            grupo = obj.groups.first()
            
        if grupo:
            descriptions = {
                'administrador': 'Administrador con acceso total al sistema',
                'empleadonivel1': 'Supervisor con permisos de gestión',
                'empleadonivel2': 'Vendedor con permisos de venta',
                'cliente': 'Cliente con acceso básico'
            }
            return {
                'id': grupo.id,
                'nombre': grupo.name,
                'descripcion': descriptions.get(grupo.name, '')
            }
        return None
        
    def to_representation(self, instance):
        """Personalizar respuesta"""
        data = super().to_representation(instance)
        data['password_temporal'] = True
        data['debe_cambiar_password'] = True
        return data


class LoginSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer vs ModelSerializer
    
    Usamos Serializer (no ModelSerializer) cuando:
    - No estamos trabajando directamente con un modelo
    - Necesitamos validación personalizada compleja
    - Los datos no corresponden 1:1 con un modelo
    - Es para operaciones como login, reset password, etc.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False  # No remover espacios (importante para contraseñas)
    )
    
    def validate(self, data):
        """Validar credenciales de login"""
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # Autenticar usuario
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Usamos email como username
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciales inválidas.',
                    code='authorization'
                )
                
            if not user.is_active:
                raise serializers.ValidationError(
                    'Cuenta desactivada.',
                    code='authorization'
                )
                
            data['user'] = user
            return data
        else:
            raise serializers.ValidationError(
                'Debe incluir email y contraseña.',
                code='authorization'
            )


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer simplificado para búsquedas"""
    
    rol = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'rol']
        
    def get_rol(self, obj):
        """Obtener nombre del rol principal"""
        grupo = obj.groups.first()
        return grupo.name if grupo else None


class UserStatsSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para datos no relacionados con modelos
    
    Útil para serializar estadísticas, reportes, o cualquier dato
    que no corresponde directamente a un modelo.
    """
    
    total_usuarios = serializers.IntegerField()
    usuarios_activos = serializers.IntegerField()
    usuarios_por_rol = serializers.DictField()
    registros_ultimo_mes = serializers.IntegerField()
    ultimo_login = serializers.DateTimeField()
    usuarios_nuevos_hoy = serializers.IntegerField()
    usuarios_inactivos = serializers.IntegerField()
