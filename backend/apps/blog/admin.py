from django.contrib import admin
from .models import BlogPost, BlogComment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor_nombre', 'publicado', 'categoria', 'fecha_publicacion')
    list_filter = ('publicado', 'categoria', 'fecha_publicacion')
    list_editable = ('publicado',)
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('autor_nombre', 'articulo_id', 'aprobado', 'fecha_creacion')
    list_filter = ('aprobado', 'fecha_creacion')
    list_editable = ('aprobado',)
    search_fields = ('autor_nombre', 'contenido')
