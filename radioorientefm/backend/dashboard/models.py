from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from apps.articulos.models import Articulo

User = get_user_model()

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('nuevo_articulo', 'Nuevo Artículo'),
        ('comentario', 'Nuevo Comentario'),
        ('sistema', 'Mensaje del Sistema'),
    ]
    
    # Usamos related_name personalizado para evitar conflictos con la app notifications
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='dashboard_notificaciones'
    )
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='sistema')
    leida = models.BooleanField(default=False)
    url = models.URLField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

# Señal para notificar cuando se crea un nuevo artículo
@receiver(post_save, sender=Articulo)
def notificar_nuevo_articulo(sender, instance, created, **kwargs):
    if created:
        from django.contrib.auth.models import User
        admin_users = User.objects.filter(is_staff=True)
        
        for user in admin_users:
            Notificacion.objects.create(
                usuario=user,
                titulo="Nuevo Artículo Creado",
                mensaje=f"Se ha creado un nuevo artículo: {instance.titulo}",
                tipo='nuevo_articulo',
                url=f'/dashboard/articulos/editar/{instance.id}/'
            )
