from django.contrib import admin
from .models import ContactMessage, Subscription

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'asunto', 'estado', 'fecha_envio')
    list_filter = ('asunto', 'estado', 'fecha_envio')
    list_editable = ('estado',)
    search_fields = ('nombre', 'correo', 'mensaje')
    readonly_fields = ('fecha_envio',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombre', 'activa', 'fecha_suscripcion')
    list_filter = ('activa', 'fecha_suscripcion')
    list_editable = ('activa',)
    search_fields = ('correo', 'nombre')
