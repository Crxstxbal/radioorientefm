from django.contrib import admin
from .models import EstacionRadio, GeneroMusical, Conductor, Programa, HorarioPrograma, ProgramaConductor

@admin.register(EstacionRadio)
class EstacionRadioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'listeners_count', 'telefono', 'email')
    search_fields = ('nombre', 'descripcion')

@admin.register(GeneroMusical)
class GeneroMusicalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'apodo', 'email', 'activo')
    list_filter = ('activo',)
    list_editable = ('activo',)
    search_fields = ('nombre', 'apellido', 'apodo', 'email')

@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    list_editable = ('activo',)
    search_fields = ('nombre', 'descripcion')

@admin.register(HorarioPrograma)
class HorarioProgramaAdmin(admin.ModelAdmin):
    list_display = ('programa', 'dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo')
    list_editable = ('activo',)

@admin.register(ProgramaConductor)
class ProgramaConductorAdmin(admin.ModelAdmin):
    list_display = ('programa', 'conductor')
    list_filter = ('programa',)
