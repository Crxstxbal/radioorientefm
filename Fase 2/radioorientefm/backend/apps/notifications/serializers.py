# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'tipo',
            'tipo_display',
            'titulo',
            'mensaje',
            'leido',
            'fecha_creacion',
            'enlace',
            'content_type',
            'object_id',
            'tiempo_transcurrido'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'tipo_display', 'tiempo_transcurrido']

    def get_tiempo_transcurrido(self, obj):
        """Retorna tiempo transcurrido en formato legible"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.fecha_creacion

        if diff < timedelta(minutes=1):
            return "Hace un momento"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"Hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"Hace {days} dia{'s' if days > 1 else ''}"
        else:
            return obj.fecha_creacion.strftime("%d/%m/%Y %H:%M")

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones"""

    class Meta:
        model = Notification
        fields = [
            'usuario',
            'tipo',
            'titulo',
            'mensaje',
            'enlace',
            'content_type',
            'object_id'
        ]
