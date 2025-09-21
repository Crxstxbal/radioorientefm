from django.db import models
from django.conf import settings

class BandaEmergente(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente de revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name="bandas"
    )

    nombre_banda = models.CharField(max_length=150)
    integrantes = models.TextField(blank=True, null=True)
    genero = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=100, blank=True, null=True)

    correo_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)

    mensaje = models.TextField()
    links = models.TextField(blank=True, null=True)
    press_kit = models.FileField(upload_to="presskits/", blank=True, null=True)

    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS,
        default='pendiente'
    )

    class Meta:
        db_table = "bandas_emergentes"
        verbose_name = "Banda Emergente"
        verbose_name_plural = "Bandas Emergentes"

    def __str__(self):
        return f"{self.nombre_banda} - {self.genero} ({self.estado})"
