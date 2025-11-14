from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Articulo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'descripcion')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'publicado', 'destacado', 'fecha_publicacion', 'vistas', 'tiene_multimedia', 'preview_thumbnails')
    list_filter = ('publicado', 'destacado', 'categoria', 'fecha_publicacion', 'fecha_creacion')
    list_editable = ('publicado', 'destacado')
    search_fields = ('titulo', 'contenido', 'resumen')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'vistas', 'imagen_destacada', 'preview_imagen_portada', 'preview_imagen_thumbnail')
    prepopulated_fields = {'slug': ('titulo',)}
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'slug', 'autor', 'categoria')
        }),
        ('Contenido', {
            'fields': ('resumen', 'contenido')
        }),
        ('Multimedia - Imágenes', {
            'fields': (
                ('imagen_portada', 'preview_imagen_portada'),
                ('imagen_thumbnail', 'preview_imagen_thumbnail'),
                'imagen_url',
                'imagen_destacada'
            ),
            'description': '<strong>📸 Imagen Portada (Banner):</strong> Horizontal 1200x400px para el modal. <br><strong>🖼️ Imagen Thumbnail:</strong> Cuadrada 600x600px para las tarjetas de noticias.'
        }),
        ('Multimedia - Otros', {
            'fields': ('video_url', 'archivo_adjunto'),
            'classes': ('collapse',)
        }),
        ('Estado y visibilidad', {
            'fields': ('publicado', 'destacado', 'fecha_publicacion')
        }),
        ('Metadatos', {
            'fields': ('vistas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_imagen_portada(self, obj):
        if obj.imagen_portada:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 100px; border-radius: 4px;" />', obj.imagen_portada.url)
        return "Sin imagen"
    preview_imagen_portada.short_description = "Vista previa Banner"
    
    def preview_imagen_thumbnail(self, obj):
        if obj.imagen_thumbnail:
            return format_html('<img src="{}" style="max-width: 150px; max-height: 150px; border-radius: 4px; object-fit: cover;" />', obj.imagen_thumbnail.url)
        return "Sin imagen"
    preview_imagen_thumbnail.short_description = "Vista previa Thumbnail"
    
    def preview_thumbnails(self, obj):
        html = ''
        if obj.imagen_thumbnail:
            html += format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 4px; object-fit: cover; margin-right: 5px;" />', obj.imagen_thumbnail.url)
        if obj.imagen_portada:
            html += format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 4px; object-fit: cover;" />', obj.imagen_portada.url)
        return html if html else "📷"
    preview_thumbnails.short_description = "Imágenes"
