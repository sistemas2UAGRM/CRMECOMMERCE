import os  # <--- Importante para leer el .env
from rest_framework import serializers
from django.db import transaction
from .models import Client, Domain
from django.contrib.auth import get_user_model

User = get_user_model()

class TenantRegisterSerializer(serializers.Serializer):
    # Datos de la tienda
    tienda_nombre = serializers.CharField(max_length=100)
    subdominio = serializers.SlugField(max_length=63) # 'pepita', 'mitienda'
    
    # Datos del usuario administrador
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_subdominio(self, value):
        # Evitar subdominios reservados
        reservados = ['www', 'api', 'admin', 'public']
        if value in reservados:
            raise serializers.ValidationError("Este subdominio no está disponible.")
        
        # Verificar si ya existe el esquema o dominio
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError("Este nombre de tienda ya está registrado.")
        return value.lower()

    def create(self, validated_data):
        schema_name = validated_data['subdominio']
        tienda_name = validated_data['tienda_nombre']
        
        with transaction.atomic():
            # 1. Crear el Cliente (Tenant)
            # Esto dispara la creación del ESQUEMA en Postgres
            tenant = Client.objects.create(
                schema_name=schema_name,
                name=tienda_name
            )

            # ==========================================================
            # 2. Crear el Dominio asociado (MODIFICADO PARA .ENV)
            # ==========================================================
            
            # Intentamos leer la IP del servidor desde las variables de entorno
            server_ip = os.getenv('SERVER_IP')

            # Si no existe la variable (ej. desarrollo local sin .env), usamos localhost
            if not server_ip:
                server_ip = '127.0.0.1'
                print("⚠️ ADVERTENCIA: No se encontró SERVER_IP en .env, usando 127.0.0.1")

            # Construimos la URL dinámica usando nip.io
            # Ejemplo resultado: pepita.54.200.10.20.nip.io
            domain_url = f"{schema_name}.{server_ip}.nip.io"
            
            Domain.objects.create(
                domain=domain_url,
                tenant=tenant,
                is_primary=True
            )
            # ==========================================================

            # 3. Crear el Usuario Admin DENTRO del nuevo esquema
            # Usamos tenant_context para cambiar temporalmente a la nueva BD
            from django_tenants.utils import tenant_context
            from django.contrib.auth.models import Group

            with tenant_context(tenant):
                # Estamos ahora en el esquema nuevo
                user = User.objects.create_user(
                    email=validated_data['email'],
                    username=validated_data['email'], # Username igual a email
                    password=validated_data['password'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    is_active=True,
                    is_staff=True,
                    is_superuser=True # Admin total de su tienda
                )
                
                # Asignar rol 'administrador' si usas grupos
                admin_group, _ = Group.objects.get_or_create(name='administrador')
                user.groups.add(admin_group)
                
        return tenant

class TenantPublicSerializer(serializers.ModelSerializer):
    domain_url = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ['name', 'schema_name', 'created_on', 'domain_url']

    def get_domain_url(self, obj):
        # Asume que el cliente tiene al menos un dominio
        domain = Domain.objects.filter(tenant=obj, is_primary=True).first()
        return domain.domain if domain else None