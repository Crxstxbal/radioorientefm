from django.db import models
from django.conf import settings

class EstacionRadio(models.Model):
    """estación de radio normalizada"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    stream_url = models.URLField(max_length=500, blank=True, null=True)
    live_stream_url = models.URLField(max_length=500, blank=True, null=True, 
                                    verbose_name='URL de transmisión en vivo',
                                    help_text='URL de YouTube, Facebook Live u otra plataforma para transmisión en vivo')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    listeners_count = models.IntegerField(default=0)
    activo = models.BooleanField(default=True, verbose_name='En el aire',
                              help_text='Indica si la estación está transmitiendo actualmente')

    class Meta:
        db_table = 'estacion_radio'
        verbose_name = 'Estación de Radio'
        verbose_name_plural = 'Estaciones de Radio'

    def __str__(self):
        return self.nombre

class GeneroMusical(models.Model):
    """géneros musicales normalizados"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'genero_musical'
        verbose_name = 'Género Musical'
        verbose_name_plural = 'Géneros Musicales'
    
    def __str__(self):
        return self.nombre

class Conductor(models.Model):
    """conductores de programas"""
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    apodo = models.CharField(max_length=150, blank=True, null=True)
    foto = models.ImageField(upload_to='locutores/', null=True, blank=True, verbose_name="Foto")
    email = models.EmailField(max_length=254, blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    
    class Meta:
        db_table = 'conductor'
        verbose_name = 'Conductor'
        verbose_name_plural = 'Conductores'
    
    def __str__(self):
        if self.apodo:
            return f"{self.nombre} '{self.apodo}' {self.apellido}"
        return f"{self.nombre} {self.apellido}"

class Programa(models.Model):
    """programas de radio normalizados"""
    estacion = models.ForeignKey(
        EstacionRadio,
        on_delete=models.SET_NULL,
        #no eliminar programas si se elimina la estación
        related_name='programas',
                  #permite valores nulos temporalmente
        null=True,
                 #permite que el campo esté en blanco en formularios
        blank=True,
        help_text='Este campo se completará automáticamente con la estación de radio existente.'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    imagen_url = models.URLField(max_length=500, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        #si no hay una estación asignada, asigna la primera estación disponible
        if not self.estacion_id:
            estacion = EstacionRadio.objects.first()
            if estacion:
                self.estacion = estacion
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'programa'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'

    def __str__(self):
        return self.nombre

    def get_dias_display(self):
        """retorna los días de la semana en formato legible"""
        dias_map = {
            0: 'Dom', 1: 'Lun', 2: 'Mar', 3: 'Mié',
            4: 'Jue', 5: 'Vie', 6: 'Sáb'
        }
        horarios = self.horarios.filter(activo=True).order_by('dia_semana')
        if not horarios:
            return "Sin horario"
        dias = [dias_map[h.dia_semana] for h in horarios]
        return ", ".join(dias)

    def get_horario_display(self):
        """retorna el horario en formato legible"""
        horarios = self.horarios.filter(activo=True).first()
        if not horarios:
            return "Sin horario"
        return f"{horarios.hora_inicio.strftime('%H:%M')} - {horarios.hora_fin.strftime('%H:%M')}"

class ProgramaConductor(models.Model):
    """relación muchos a muchos entre programas y conductores"""
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='conductores')
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='programas')
    
    class Meta:
        db_table = 'programa_conductor'
        unique_together = ['programa', 'conductor']
        verbose_name = 'Programa-Conductor'
        verbose_name_plural = 'Programas-Conductores'
    
    def __str__(self):
        return f"{self.programa.nombre} - {self.conductor}"

class HorarioPrograma(models.Model):
    """horarios de programas"""
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(
        choices=[
            (0, 'Domingo'), (1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'),
            (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado')
        ]
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'horario_programa'
        ordering = ['dia_semana', 'hora_inicio']
        verbose_name = 'Horario de Programa'
        verbose_name_plural = 'Horarios de Programas'

    def __str__(self):
        days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        day_name = days[self.dia_semana]
        return f"{self.programa.nombre} - {day_name} {self.hora_inicio}-{self.hora_fin}"

class ReproduccionRadio(models.Model):
    """seguimiento de reproducciones únicas de la radio"""
    estacion = models.ForeignKey(EstacionRadio, on_delete=models.CASCADE, related_name='reproducciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reproducciones_radio')
    fecha_reproduccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reproduccion_radio'
        verbose_name = 'Reproducción de Radio'
        verbose_name_plural = 'Reproducciones de Radio'
        unique_together = ['estacion', 'usuario']
        indexes = [
            models.Index(fields=['estacion']),
            models.Index(fields=['usuario']),
            models.Index(fields=['fecha_reproduccion']),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.estacion.nombre} - {self.fecha_reproduccion}"
