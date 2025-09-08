from django.db import models

class ContactMessage(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20, blank=True)
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='nuevo')

    class Meta:
        db_table = 'formulario_contacto'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"

class Subscription(models.Model):
    correo = models.CharField(max_length=150, unique=True)
    nombre = models.CharField(max_length=100, blank=True)
    activa = models.BooleanField(default=True)
    fecha_suscripcion = models.DateTimeField(auto_now_add=True)
    token_unsuscribe = models.CharField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'suscripciones'
        ordering = ['-fecha_suscripcion']

    def __str__(self):
        return self.correo
