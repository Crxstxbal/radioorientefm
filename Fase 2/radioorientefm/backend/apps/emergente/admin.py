from django.contrib import admin
from .models import Integrante, BandaEmergente, BandaLink, BandaIntegrante

@admin.register(Integrante)
class IntegranteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

class BandaLinkInline(admin.TabularInline):
    model = BandaLink
    extra = 1

class BandaIntegranteInline(admin.TabularInline):
    model = BandaIntegrante
    extra = 1

@admin.register(BandaEmergente)
class BandaEmergenteAdmin(admin.ModelAdmin):
    list_display = ('nombre_banda', 'genero', 'email_contacto', 'estado', 'fecha_envio')
    list_filter = ('genero', 'estado', 'fecha_envio')
    search_fields = ('nombre_banda', 'email_contacto')
    readonly_fields = ('fecha_envio',)
    inlines = [BandaLinkInline, BandaIntegranteInline]

@admin.register(BandaLink)
class BandaLinkAdmin(admin.ModelAdmin):
    list_display = ('banda', 'tipo', 'url')
    list_filter = ('tipo',)
    search_fields = ('banda__nombre_banda', 'tipo') 
