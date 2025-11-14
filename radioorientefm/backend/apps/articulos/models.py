from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
import os
from datetime import datetime


def upload_to_articulos_imagen(instance, filename):
    """Guarda imágenes en: MEDIA_ROOT/articulos/imagenes/YYYY/MM/filename"""
    ext = filename.split('.')[-1]
    # Usar el slug si existe, o un timestamp si aún no se ha generado
    slug = instance.slug if instance.slug else f"articulo-{timezone.now().timestamp()}"
    filename = f"{slug}.{ext}"
    # Usar la fecha actual en lugar de fecha_creacion que puede no existir aún
    now = timezone.now()
    return os.path.join('articulos', 'imagenes', now.strftime('%Y/%m'), filename)


def upload_to_articulos_archivo(instance, filename):
    """Guarda archivos adjuntos en: MEDIA_ROOT/articulos/archivos/YYYY/MM/filename"""
    # Usar la fecha actual en lugar de fecha_creacion que puede no existir aún
    now = timezone.now()
    return os.path.join('articulos', 'archivos', now.strftime('%Y/%m'), filename)


class Categoria(models.Model):
    """Categorías de artículos normalizadas"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    
    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nombre


class Articulo(models.Model):
    """Artículos con soporte para multimedia"""
    titulo = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    contenido = models.TextField(verbose_name='Contenido')
    resumen = models.TextField(blank=True, null=True, verbose_name='Resumen')
    
    # Campos multimedia
    imagen_portada = models.ImageField(
        upload_to=upload_to_articulos_imagen,
        null=True,
        blank=True,
        verbose_name='Imagen Banner (Horizontal)',
        help_text='Imagen horizontal para modal/detalle (1200x400px recomendado)'
    )
    imagen_thumbnail = models.ImageField(
        upload_to=upload_to_articulos_imagen,
        null=True,
        blank=True,
        verbose_name='Imagen Miniatura (Cuadrada)',
        help_text='Imagen cuadrada para tarjetas de lista (600x600px recomendado)'
    )
    imagen_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name='URL de imagen externa',
        help_text='Alternativa: URL de imagen externa (se usa si no hay imagen subida)'
    )
    video_url = models.URLField(
        blank=True, 
        null=True,
        verbose_name='URL de video',
        help_text='YouTube, Vimeo, etc. (opcional)'
    )
    archivo_adjunto = models.FileField(
        upload_to=upload_to_articulos_archivo,
        null=True,
        blank=True,
        verbose_name='Archivo adjunto',
        help_text='PDF, Word, Excel, etc. (opcional, máx 10MB)'
    )
    
    # Relaciones
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='articulos',
        verbose_name='Autor'
    )
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articulos',
        verbose_name='Categoría'
    )
    
    # Estados
    publicado = models.BooleanField(default=False, verbose_name='Publicado')
    destacado = models.BooleanField(default=False, verbose_name='Destacado')
    
    # Fechas
    fecha_publicacion = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    
    # Metadatos
    vistas = models.PositiveIntegerField(default=0, verbose_name='Vistas')
    usuarios_que_vieron = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='articulos_vistos',
        blank=True,
        verbose_name='Usuarios que vieron este artículo'
    )

    class Meta:
        db_table = 'articulo'
        ordering = ['-fecha_publicacion', '-fecha_creacion']
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'
        indexes = [
            models.Index(fields=['publicado']),
            models.Index(fields=['slug']),
            models.Index(fields=['autor']),
            models.Index(fields=['categoria']),
            models.Index(fields=['-fecha_publicacion']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    
    @property
    def imagen_destacada(self):
        """Retorna la URL de la imagen, priorizando imagen subida sobre URL externa"""
        if self.imagen_portada:
            return self.imagen_portada.url
        return self.imagen_url
    
    @property
    def tiene_multimedia(self):
        """Verifica si el artículo tiene contenido multimedia"""
        return bool(self.imagen_portada or self.imagen_url or self.video_url or self.archivo_adjunto)

    def __str__(self):
        return self.titulo
