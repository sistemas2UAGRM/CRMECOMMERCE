#core/users/models.py
from django.db import models  
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
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
   sexo = models.CharField(max_length=20, null=True, blank=True)
   celular = models.CharField(max_length=20, null=True, blank=True)
   groups = models.ManyToManyField(
      Group,
      verbose_name='groups',
      blank=True,
      help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
      related_name="user_set_custom",  # Nombre único para la relación inversa
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
      return self.get_full_name() if self.first_name else self.username

class UserProfile(models.Model):
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
    # JSONField es ideal para guardar configuraciones flexibles
    preferencias_ui = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuraciones de UI como tema, fuente, etc."
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"

# ¡NUEVO! Modelo para Direcciones
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
    nombre_completo = models.CharField(max_length=255)
    linea1 = models.CharField("Dirección Línea 1", max_length=255)
    linea2 = models.CharField("Dirección Línea 2", max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    pais = models.CharField(max_length=50, default="Bolivia")
    telefono_contacto = models.CharField(max_length=20)
    es_predeterminada = models.BooleanField(default=False)

    def __str__(self):
        return f"Dirección de {self.user.username} - {self.linea1}"