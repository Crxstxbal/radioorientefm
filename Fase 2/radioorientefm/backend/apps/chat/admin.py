from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'usuario_nombre', 'sala', 'contenido', 'tipo', 'fecha_envio')
    list_filter = ('sala', 'tipo', 'fecha_envio')
    search_fields = ('usuario_nombre', 'contenido')
    readonly_fields = ('fecha_envio',)
