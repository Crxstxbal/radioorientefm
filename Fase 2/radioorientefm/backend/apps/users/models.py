from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Usuario personalizado que sigue la estructura de PostgreSQL normalizada
    pero mantiene compatibilidad con Django Auth
    """
    # Campos principales (siguiendo el esquema PostgreSQL)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    
    # Campos de Django Auth
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # Campo para bloquear chat
    chat_bloqueado = models.BooleanField(default=False, verbose_name='Chat Bloqueado')
    
    # Manager personalizado
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    # Propiedades para compatibilidad con código anterior
    @property
    def correo(self):
        return self.email

    @correo.setter
    def correo(self, value):
        # Permitir asignar correo desde código antiguo (e.g., user.correo = ...)
        if value is None:
            self.email = ''
        else:
            self.email = value

    @property
    def usuario(self):
        return self.username

    @usuario.setter
    def usuario(self, value):
        # Permitir asignar username desde código antiguo (e.g., user.usuario = ...)
        if value is None:
            self.username = ''
        else:
            self.username = value

    @property
    def nombre(self):
        return self.full_name

    @nombre.setter
    def nombre(self, value):
        # Permitir asignar el nombre completo (e.g., user.nombre = "Juan Pérez")
        # Se divide en first_name y last_name: primer token -> first_name, resto -> last_name
        if not value:
            self.first_name = ''
            self.last_name = ''
            return
        parts = str(value).strip().split()
        if len(parts) == 1:
            self.first_name = parts[0]
            self.last_name = ''
        else:
            self.first_name = parts[0]
            self.last_name = ' '.join(parts[1:])
