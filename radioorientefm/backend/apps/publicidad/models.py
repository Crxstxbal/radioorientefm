from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# ==========================
# Base Models
# ==========================

class Publicidad(models.Model):
    """Modelo base para todas las publicidades"""
    TIPO_CHOICES = [
        ('WEB', 'Web'),
        ('RADIAL', 'Radial'),
    ]
    
    nombre_cliente = models.CharField(max_length=150, verbose_name="Nombre del Cliente")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Publicidad")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Finalización")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?")
    costo_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Costo Total"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        db_table = 'publicidad'
        verbose_name = 'Publicidad'
        verbose_name_plural = 'Publicidades'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['activo']),
            models.Index(fields=['fecha_inicio', 'fecha_fin']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
                name='publicidad_fechas_validas'
            )
        ]
    
    def __str__(self):
        return f"{self.nombre_cliente} - {self.get_tipo_display()}"

# ==========================
# Modelos para Publicidad Web
# ==========================

class PublicidadWeb(models.Model):
    """Información específica para publicidad web"""
    publicidad = models.OneToOneField(
        Publicidad, 
        on_delete=models.CASCADE, 
        related_name='web_config',
        limit_choices_to={'tipo': 'WEB'}
    )
    url_destino = models.URLField(max_length=500, verbose_name="URL de Destino")
    formato = models.CharField(max_length=200, verbose_name="Formato (ej: 728x90)")
    impresiones = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Número de Impresiones"
    )
    clics = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Número de Clics"
    )
    archivo_media = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name="URL del Archivo Multimedia"
    )
    
    class Meta:
        db_table = 'publicidad_web'
        verbose_name = 'Configuración Web'
        verbose_name_plural = 'Configuraciones Web'
    
    def __str__(self):
        return f"Web - {self.publicidad.nombre_cliente}"

class TipoUbicacion(models.Model):
    """Tipos de ubicaciones disponibles para publicidad"""
    codigo = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Código del Tipo",
        help_text="Identificador único en minúsculas y sin espacios (ej: banner_principal)"
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Tipo",
        help_text="Nombre descriptivo del tipo de ubicación"
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Descripción detallada de este tipo de ubicación"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activo?",
        help_text="¿Este tipo de ubicación está disponible para su uso?"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tipo de Ubicación'
        verbose_name_plural = 'Tipos de Ubicación'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class UbicacionPublicidadWeb(models.Model):
    """Catálogo de ubicaciones disponibles para publicidad web"""
    
    nombre = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Nombre de la Ubicación"
    )
    tipo = models.ForeignKey(
        'TipoUbicacion',
        on_delete=models.PROTECT,
        related_name='ubicaciones',
        verbose_name="Tipo de Ubicación"
    )
    descripcion = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Descripción"
    )
    dimensiones = models.CharField(
        max_length=50, 
        verbose_name="Dimensiones",
        help_text="Ej: 300x600, 728x90"
    )
    precio_mensual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Mensual"
    )
    activo = models.BooleanField(
        default=True, 
        help_text="¿Está disponible para contratar?",
        verbose_name="¿Activo?"
    )
    orden = models.IntegerField(
        default=0, 
        help_text="Orden de visualización en catálogo",
        verbose_name="Orden"
    )
    
    class Meta:
        db_table = 'ubicacion_publicidad_web'
        verbose_name = 'Ubicación de Publicidad Web'
        verbose_name_plural = 'Ubicaciones de Publicidad Web'
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.dimensiones})"

class SolicitudPublicidadWeb(models.Model):
    """Solicitud de publicidad web enviada por un usuario"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('activa', 'Activa (publicándose)'),
        ('finalizada', 'Finalizada'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='solicitudes_publicidad_web',
        verbose_name="Usuario"
    )
    
    # Datos de contacto del solicitante
    nombre_contacto = models.CharField(max_length=150, verbose_name="Nombre de Contacto")
    email_contacto = models.EmailField(verbose_name="Email de Contacto")
    telefono_contacto = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name="Teléfono de Contacto"
    )
    
    PREFERENCIA_CHOICES = [
        ('telefono', 'Teléfono'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    ]
    preferencia_contacto = models.CharField(
        max_length=20, 
        choices=PREFERENCIA_CHOICES, 
        default='telefono',
        verbose_name="Preferencia de Contacto"
    )
    
    # Estado y seguimiento
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Solicitud")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_publicidad_web_aprobadas',
        verbose_name="Aprobado por"
    )
    fecha_aprobacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha de Aprobación"
    )
    publicacion = models.OneToOneField(
        Publicidad,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='solicitud_web',
        limit_choices_to={'tipo':'WEB'},
        verbose_name="Campaña Publicada"
    )
    
    # Fechas de publicación solicitadas
    fecha_inicio_solicitada = models.DateField(verbose_name="Fecha de Inicio Solicitada")
    fecha_fin_solicitada = models.DateField(verbose_name="Fecha de Finalización Solicitada")
    
    # Notas y observaciones
    mensaje_usuario = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Mensaje del Usuario",
        help_text="Mensaje o comentarios del usuario"
    )
    notas_admin = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Notas del Administrador",
        help_text="Notas internas del administrador"
    )
    motivo_rechazo = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Motivo de Rechazo"
    )
    
    # Totales
    costo_total_estimado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Costo Total Estimado"
    )
    
    class Meta:
        db_table = 'solicitud_publicidad_web'
        verbose_name = 'Solicitud de Publicidad Web'
        verbose_name_plural = 'Solicitudes de Publicidad Web'
        ordering = ['-fecha_solicitud']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_solicitud']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(fecha_fin_solicitada__gte=models.F('fecha_inicio_solicitada')),
                name='solicitud_web_fechas_validas'
            )
        ]
    
    def __str__(self):
        return f"Solicitud Web #{self.id} - {self.usuario.email} ({self.get_estado_display()})"

class ItemSolicitudWeb(models.Model):
    """Cada ubicación/espacio publicitario web dentro de una solicitud"""
    solicitud = models.ForeignKey(
        SolicitudPublicidadWeb, 
        on_delete=models.CASCADE, 
        related_name='items_web',
        verbose_name="Solicitud"
    )
    ubicacion = models.ForeignKey(
        UbicacionPublicidadWeb, 
        on_delete=models.PROTECT, 
        related_name='items_solicitud_web',
        verbose_name="Ubicación"
    )
    url_destino = models.URLField(
        max_length=500, 
        verbose_name="URL de Destino",
        help_text="Link al que redirige la publicidad"
    )
    formato = models.CharField(
        max_length=50, 
        verbose_name="Formato",
        help_text="Dimensiones del banner (ej: 728x90)"
    )
    precio_acordado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Acordado"
    )
    notas = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Notas"
    )
    
    class Meta:
        db_table = 'item_solicitud_web'
        verbose_name = 'Item de Solicitud Web'
        verbose_name_plural = 'Items de Solicitud Web'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.ubicacion.nombre} - {self.formato} (${self.precio_acordado})"

class ImagenPublicidadWeb(models.Model):
    """Imágenes asociadas a cada item de solicitud web"""
    item = models.ForeignKey(
        ItemSolicitudWeb, 
        on_delete=models.CASCADE, 
        related_name='imagenes_web',
        verbose_name="Item de Solicitud"
    )
    imagen = models.ImageField(
        upload_to='publicidad/web/solicitudes/%Y/%m/', 
        verbose_name="Archivo de Imagen",
        help_text="Imagen para la publicidad web"
    )
    descripcion = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name="Descripción"
    )
    orden = models.IntegerField(
        default=0, 
        help_text="Orden de visualización si hay múltiples imágenes",
        verbose_name="Orden"
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Subida"
    )
    
    class Meta:
        db_table = 'imagen_publicidad_web'
        verbose_name = 'Imagen de Publicidad Web'
        verbose_name_plural = 'Imágenes de Publicidad Web'
        ordering = ['orden', 'fecha_subida']
    
    def __str__(self):
        return f"Imagen {self.id} - {self.item}"

# ==========================
# Modelos para Publicidad Radial
# ==========================

class PublicidadRadial(models.Model):
    """Información específica para publicidad radial"""
    publicidad = models.OneToOneField(
        Publicidad,
        on_delete=models.CASCADE,
        related_name='radial_config',
        limit_choices_to={'tipo': 'RADIAL'}
    )
    
    # Información del spot radial
    duracion = models.IntegerField(
        verbose_name="Duración en segundos",
        help_text="Duración del spot en segundos"
    )
    
    # Frecuencia de reproducción
    repeticiones_diarias = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Repeticiones diarias"
    )
    
    # Archivo de audio
    archivo_audio = models.FileField(
        upload_to='publicidad/radial/audios/%Y/%m/',
        verbose_name="Archivo de Audio",
        help_text="Archivo de audio para la publicidad radial"
    )
    
    # Estadísticas
    reproducciones = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Número de Reproducciones"
    )
    
    class Meta:
        db_table = 'publicidad_radial'
        verbose_name = 'Configuración Radial'
        verbose_name_plural = 'Configuraciones Radiales'
    
    def __str__(self):
        return f"Radial - {self.publicidad.nombre_cliente}"
