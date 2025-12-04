#-*- coding: utf-8 -*-
from django.db import models
from django.conf import settings

class Notification(models.Model):
    """modelo para notificaciones del sistema"""

    TIPO_CHOICES = [
        ('contacto', 'Mensaje de Contacto'),
        ('banda', 'Banda Emergente'),
        ('articulo', 'Articulo Nuevo'),
        ('programa', 'Cambio en Programacion'),
        ('suscripcion', 'Nueva Suscripcion'),
        ('publicidad', 'Solicitud de Publicidad'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    enlace = models.CharField(max_length=255, blank=True, null=True)

    #referencia opcional al objeto que genero la notificacion
    content_type = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leido']),
            models.Index(fields=['fecha_creacion']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.titulo} ({'Leida' if self.leido else 'No leida'})"

    def marcar_como_leido(self):
        """marca la notificacion como leida"""
        self.leido = True
        self.save(update_fields=['leido'])
