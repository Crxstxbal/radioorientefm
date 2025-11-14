from django.contrib import admin
from .models import TipoAsunto, Estado, Contacto, Suscripcion

@admin.register(TipoAsunto)
class TipoAsuntoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_entidad', 'descripcion')
    list_filter = ('tipo_entidad',)
    search_fields = ('nombre',)

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'tipo_asunto', 'estado', 'fecha_envio')
    list_filter = ('tipo_asunto', 'estado', 'fecha_envio')
    list_editable = ('estado',)
    search_fields = ('nombre', 'email', 'mensaje')
    readonly_fields = ('fecha_envio',)

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombre', 'activa', 'fecha_suscripcion')
    list_filter = ('activa', 'fecha_suscripcion')
    list_editable = ('activa',)
    search_fields = ('email', 'nombre')
    readonly_fields = ('token_unsuscribe', 'fecha_suscripcion')
