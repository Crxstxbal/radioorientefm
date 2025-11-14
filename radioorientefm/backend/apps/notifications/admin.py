# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'usuario', 'leido', 'fecha_creacion']
    list_filter = ['tipo', 'leido', 'fecha_creacion']
    search_fields = ['titulo', 'mensaje', 'usuario__email']
    readonly_fields = ['fecha_creacion']
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']

    fieldsets = (
        ('Informacion Basica', {
            'fields': ('usuario', 'tipo', 'titulo', 'mensaje')
        }),
        ('Estado y Enlace', {
            'fields': ('leido', 'enlace', 'fecha_creacion')
        }),
        ('Referencia', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Las notificaciones se crean automaticamente con signals
        return False
