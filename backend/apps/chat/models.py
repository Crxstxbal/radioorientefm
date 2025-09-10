from django.db import models

class ChatMessage(models.Model):
    id_usuario = models.IntegerField()
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    usuario_nombre = models.CharField(max_length=100, blank=True, null=True)
    tipo = models.CharField(max_length=20, default='user')
    sala = models.CharField(max_length=50, default='general')

    class Meta:
        db_table = 'mensajes'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.usuario_nombre or self.id_usuario}: {self.contenido[:50]}..."
