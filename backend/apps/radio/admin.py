from django.contrib import admin
from .models import RadioStation, Program, News

@admin.register(RadioStation)
class RadioStationAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa', 'listeners_count')
    list_editable = ('activa',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('nombre_programa', 'conductor', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo')
    list_editable = ('activo',)
    search_fields = ('nombre_programa', 'conductor')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor_nombre', 'destacada', 'publicada', 'fecha_publicacion')
    list_filter = ('destacada', 'publicada', 'fecha_publicacion')
    list_editable = ('destacada', 'publicada')
    search_fields = ('titulo', 'contenido')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
