from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Role(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'roles'
    
    def __str__(self):
        return self.nombre

class UserManager(BaseUserManager):
    def create_user(self, correo, usuario, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, usuario=usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, usuario, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(correo, usuario, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    nombre = models.TextField()
    usuario = models.TextField(unique=True)
    correo = models.TextField(unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    rol_id = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    
    # Campos requeridos por Django
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['usuario', 'nombre']
    
    class Meta:
        db_table = 'usuarios'
    
    def __str__(self):
        return f"{self.nombre} ({self.correo})"
    
    @property
    def full_name(self):
        return self.nombre
    
    @property
    def email(self):
        return self.correo
    
    @property
    def username(self):
        return self.usuario
