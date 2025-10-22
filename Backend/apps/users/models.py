#apps/users/models.py
import uuid
from django.db import models, transaction 
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        if not password:
            raise ValueError('El usuario debe tener contraseña')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', False)
        if extra_fields.get('is_active') is False:
            extra_fields.setdefault('is_verified', False)

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) 
        extra_fields.setdefault('is_verified', True)

        if not password:
            raise ValueError('Superuser debe tener contraseña')
        return self.create_user(email, username, password, **extra_fields)
    
class User(AbstractUser):
   SEXO_OPCIONES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
   )
   email = models.EmailField(unique=True, verbose_name="Correo Electronico")
   fecha_de_nacimiento = models.DateField(null=True, blank=True)
   sexo = models.CharField(max_length=1,choices=SEXO_OPCIONES, null=True, blank=True)
   celular = models.CharField(max_length=20, null=True, blank=True)
   is_verified = models.BooleanField(
        default=False,
        help_text="Indica si el usuario ha verificado su correo electrónico."
   )
   verification_uuid = models.UUIDField(
        default=uuid.uuid4,
        help_text="Token único para la verificación de email."
   )
   acepta_marketing = models.BooleanField(
        default=False,
        help_text="Indica si el usuario acepta recibir correos de marketing."
   )
   groups = models.ManyToManyField(
      Group,
      verbose_name='groups',
      blank=True,
      help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
      related_name="user_set_custom",  
      related_query_name="user",
   )
   user_permissions = models.ManyToManyField(
      Permission,
      verbose_name='user permissions',
      blank=True,
      help_text='Specific permissions for this user.',
      related_name="user_permissions_custom", # Nombre único para la relación inversa
      related_query_name="user",
   )
   objects = UserManager()
   USERNAME_FIELD = 'email'
   REQUIRED_FIELDS = ['username', 'first_name']

   def __str__(self):
      return self.get_full_name() if self.first_name else self.email

class UserProfile(models.Model):
    TIPO_DOC_FISCAL = (
        ('CI', 'Cédula de Identidad'),
        ('NIT', 'Número de Identificación Tributaria'),
        ('PAS', 'Pasaporte'),
        ('OTRO', 'Otro'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    foto_perfil = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL de la imagen de perfil (ej. de Cloudinary)"
    )
    razon_social = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Nombre legal o de empresa para facturación"
    )
    tipo_documento_fiscal = models.CharField(
        max_length=4,
        choices=TIPO_DOC_FISCAL,
        blank=True,
        null=True
    )
    numero_documento_fiscal = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="CI, NIT, RUC, etc."
    )
    # JSONField es ideal para guardar configuraciones flexibles
    preferencias_ui = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuraciones de UI como tema, fuente, etc."
    )

    def __str__(self):
        return f"Perfil de {self.user.email}"

class Direccion(models.Model):
    TIPO_DIRECCION = (
        ('envio', 'Envío'),
        ('facturacion', 'Facturación'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='direcciones'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_DIRECCION, default='envio')
    nombre_destinatario = models.CharField(max_length=255, help_text="Nombre de la persona que recibirá el pedido.")
    linea1 = models.CharField("Dirección Línea 1", max_length=255)
    linea2 = models.CharField("Dirección Línea 2", max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = CountryField(default="BO", verbose_name="País")
    telefono_contacto = PhoneNumberField(
        blank=True, 
        help_text="Teléfono de contacto para la entrega."
    )
    es_predeterminada = models.BooleanField(default=False)
    instrucciones_adicionales = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
        ordering = ['-es_predeterminada']

    def __str__(self):
        return f"Dirección de {self.user.email} - {self.linea1}"
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Sobrescribe 'save' para asegurar que solo una dirección de
        un tipo específico ('envio' o 'facturacion') sea la predeterminada.
        """
        if self.es_predeterminada:
            # Selecciona todas las OTRAS direcciones del MISMO usuario y MISMO tipo
            qs = Direccion.objects.filter(
                user=self.user, 
                tipo=self.tipo
            ).exclude(pk=self.pk)
            
            # Y les quita la marca 'predeterminada'
            qs.update(es_predeterminada=False)
        
        super(Direccion, self).save(*args, **kwargs)