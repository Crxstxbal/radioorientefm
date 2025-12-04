from django.db import models
from django.conf import settings

class Integrante(models.Model):
    """integrantes de bandas normalizados"""
    nombre = models.CharField(max_length=150)
    
    class Meta:
        db_table = 'integrante'
        verbose_name = 'Integrante'
        verbose_name_plural = 'Integrantes'
    
    def __str__(self):
        return self.nombre

class BandaEmergente(models.Model):
    """bandas emergentes normalizadas"""
    nombre_banda = models.CharField(max_length=150)
    email_contacto = models.EmailField(max_length=254)
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)
    mensaje = models.TextField()
    documento_presentacion = models.URLField(max_length=500, blank=True, null=True)
    
    #relaciones normalizadas
    genero = models.ForeignKey('radio.GeneroMusical', on_delete=models.CASCADE, related_name='bandas_emergentes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bandas_emergentes')
    estado = models.ForeignKey('contact.Estado', on_delete=models.CASCADE, related_name='bandas_emergentes')
    comuna = models.ForeignKey('ubicacion.Comuna', on_delete=models.SET_NULL, null=True, blank=True, related_name='bandas_emergentes')
    
    #fechas y seguimiento
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_revision = models.DateTimeField(blank=True, null=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='bandas_revisadas'
    )

    class Meta:
        db_table = 'banda_emergente'
        verbose_name = 'Banda Emergente'
        verbose_name_plural = 'Bandas Emergentes'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['genero']),
            models.Index(fields=['usuario']),
            models.Index(fields=['comuna']),
        ]

    def __str__(self):
        return f"{self.nombre_banda} - {self.genero.nombre}"

class BandaLink(models.Model):
    """links de bandas emergentes"""
    banda = models.ForeignKey(BandaEmergente, on_delete=models.CASCADE, related_name='links')
    tipo = models.CharField(max_length=50)  # 'spotify', 'youtube', 'instagram', etc.
    url = models.URLField(max_length=500)
    
    class Meta:
        db_table = 'banda_link'
        verbose_name = 'Link de Banda'
        verbose_name_plural = 'Links de Bandas'
    
    def __str__(self):
        return f"{self.banda.nombre_banda} - {self.tipo}"

class BandaIntegrante(models.Model):
    """relación muchos a muchos entre bandas e integrantes"""
    banda = models.ForeignKey(BandaEmergente, on_delete=models.CASCADE, related_name='integrantes')
    integrante = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name='bandas')
    
    class Meta:
        db_table = 'banda_integrante'
        unique_together = ['banda', 'integrante']
        verbose_name = 'Banda-Integrante'
        verbose_name_plural = 'Bandas-Integrantes'
    
    def __str__(self):
        return f"{self.banda.nombre_banda} - {self.integrante.nombre}"
