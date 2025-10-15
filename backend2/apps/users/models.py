#core/users/models.py
from django.db import models  
from django.contrib.auth.models import AbstractUser, Group, Permission

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
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
   #Campos de AbstractUser que ya existem :
   # username, firt_name(para nombre), email, is_active(para estado)
   # ..., password(para contrasena)
   
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
   # Hacemos que el email sea el campo para iniciar sesion
   USERNAME_FIELD = 'email'
   # Campos requeridos al crear un SUperoUsuario
   REQUIRED_FIELDS = ['username', 'first_name']

   def __str__(self):
      return self.get_full_name() if self.first_name else self.username


   
