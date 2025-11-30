from django.db import models
from django.conf import settings
import uuid

class TipoAsunto(models.Model):
    """Tipos de asunto para contactos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tipo_asunto'
        verbose_name = 'Tipo de Asunto'
        verbose_name_plural = 'Tipos de Asunto'
    
    def __str__(self):
        return self.nombre

class Estado(models.Model):
    """Estados para contactos y bandas"""
    TIPO_ENTIDAD_CHOICES = [
        ('contacto', 'Contacto'),
        ('banda', 'Banda'),
    ]
    
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    tipo_entidad = models.CharField(max_length=20, choices=TIPO_ENTIDAD_CHOICES)
    
    class Meta:
        db_table = 'estado'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_entidad_display()})"

class Contacto(models.Model):
    """Mensajes de contacto normalizados"""
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo_asunto = models.ForeignKey(TipoAsunto, on_delete=models.CASCADE, related_name='contactos')
    mensaje = models.TextField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contactos')
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='contactos')
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='contactos_respondidos'
    )

    class Meta:
        db_table = 'contacto'
        ordering = ['-fecha_envio']
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_envio']),
            models.Index(fields=['usuario']),
            models.Index(fields=['tipo_asunto']),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.tipo_asunto.nombre}"

class Suscripcion(models.Model):
    """Suscripciones normalizadas"""
    email = models.EmailField(max_length=254, unique=True)
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField(default=True)
    fecha_suscripcion = models.DateTimeField(auto_now_add=True)
    fecha_baja = models.DateTimeField(blank=True, null=True)
    token_unsuscribe = models.CharField(max_length=100, unique=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='suscripciones')

    class Meta:
        db_table = 'suscripcion'
        ordering = ['-fecha_suscripcion']
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        indexes = [
            models.Index(fields=['activa']),
            models.Index(fields=['email']),
        ]

    def save(self, *args, **kwargs):
        if not self.token_unsuscribe:
            self.token_unsuscribe = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
