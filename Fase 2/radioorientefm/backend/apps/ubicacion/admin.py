from django.contrib import admin
from .models import Pais, Ciudad, Comuna

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'pais']
    list_filter = ['pais']
    search_fields = ['nombre', 'pais__nombre']

@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'get_pais']
    list_filter = ['ciudad__pais', 'ciudad']
    search_fields = ['nombre', 'ciudad__nombre', 'ciudad__pais__nombre']
    
    def get_pais(self, obj):
        return obj.ciudad.pais.nombre
    get_pais.short_description = 'País'
