from django.db import models
from django.conf import settings

class ChatMessage(models.Model):
    #relación con usuario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_chat',
        db_column='id_usuario',
        help_text="Usuario que envió el mensaje"
    )
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    usuario_nombre = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=20, default='user')
    sala = models.CharField(max_length=50, default='general')

    class Meta:
        db_table = 'mensajes'
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['fecha_envio']),
            models.Index(fields=['sala']),
        ]

    def __str__(self):
        return f"{self.usuario_nombre or self.usuario.username}: {self.contenido[:50]}..."

    @property
    def id_usuario(self):
        """propiedad de compatibilidad para codigo existente"""
        return self.usuario_id


class ContentFilterConfig(models.Model):
    """configuracion del filtro automatico de contenido ofensivo"""
    activo = models.BooleanField(default=True, help_text="Activar/desactivar filtro automático")
    umbral_toxicidad = models.FloatField(
        default=0.7,
        help_text="Umbral de toxicidad (0.0 - 1.0). Mayor = más estricto"
    )
    bloquear_enlaces = models.BooleanField(default=False, help_text="Bloquear mensajes con enlaces")
    modo_accion = models.CharField(
        max_length=20,
        choices=[
            ('bloquear', 'Bloquear mensaje'),
            ('advertir', 'Advertir usuario'),
            ('revisar', 'Marcar para revisión')
        ],
        default='bloquear',
        help_text="Acción a tomar cuando se detecta contenido ofensivo"
    )
    strikes_para_bloqueo = models.IntegerField(
        default=3,
        help_text="Número de infracciones antes de bloquear usuario"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'filtro_contenido_config'
        verbose_name = 'Configuración de Filtro'
        verbose_name_plural = 'Configuraciones de Filtro'

    def __str__(self):
        return f"Filtro {'Activo' if self.activo else 'Inactivo'} - Umbral: {self.umbral_toxicidad}"

    @classmethod
    def get_config(cls):
        """obtener o crear configuracion única"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class PalabraProhibida(models.Model):
    """lista de palabras prohibidas personalizada"""
    palabra = models.CharField(max_length=100, unique=True)
    severidad = models.CharField(
        max_length=10,
        choices=[
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta')
        ],
        default='media'
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'palabras_prohibidas'
        verbose_name = 'Palabra Prohibida'
        verbose_name_plural = 'Palabras Prohibidas'
        ordering = ['palabra']

    def __str__(self):
        return f"{self.palabra} ({self.severidad})"


class InfraccionUsuario(models.Model):
    """registro de infracciones de usuarios"""
    #relación con usuario (siempre necesaria)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='infracciones_chat',
        db_column='id_usuario',
        help_text="Usuario que cometió la infracción"
    )
    #relacion con mensaje opcional
    mensaje = models.ForeignKey(
        ChatMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='infracciones',
        help_text="Mensaje que causó la infracción (null si fue bloqueado)"
    )
    #relacion con palabra prohibida
    palabra_prohibida = models.ForeignKey(
        'PalabraProhibida',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='infracciones',
        help_text="Palabra prohibida detectada (si aplica)"
    )
    usuario_nombre = models.CharField(max_length=100)
    mensaje_original = models.TextField()
    tipo_infraccion = models.CharField(
        max_length=50,
        choices=[
            ('toxicidad_ml', 'Toxicidad detectada por ML'),
            ('palabra_prohibida', 'Palabra prohibida'),
            ('enlace_prohibido', 'Enlace prohibido'),
            ('spam', 'Spam')
        ]
    )
    score_toxicidad = models.FloatField(null=True, blank=True, help_text="Score del modelo ML (0.0 - 1.0)")
    fecha_infraccion = models.DateTimeField(auto_now_add=True)
    accion_tomada = models.CharField(max_length=50)

    class Meta:
        db_table = 'infracciones_usuario'
        verbose_name = 'Infracción de Usuario'
        verbose_name_plural = 'Infracciones de Usuarios'
        ordering = ['-fecha_infraccion']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['fecha_infraccion']),
            models.Index(fields=['tipo_infraccion']),
            models.Index(fields=['palabra_prohibida']),
        ]

    def __str__(self):
        return f"{self.usuario_nombre} - {self.tipo_infraccion} - {self.fecha_infraccion}"

    @property
    def id_usuario(self):
        """propiedad de compatibilidad para codigo existente"""
        return self.usuario_id
