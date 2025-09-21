from django.contrib import admin
from .models import BandaEmergente

@admin.register(BandaEmergente)
class BandaEmergenteAdmin(admin.ModelAdmin):
    list_display = ('nombre_banda', 'genero', 'correo_contacto', 'fecha_envio', 'estado')  # ← cambias 'revisado' por 'estado'
    search_fields = ('nombre_banda', 'genero', 'correo_contacto')
    list_filter = ('genero', 'estado') 
