from django.db import models

class RadioStation(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    stream_url = models.CharField(max_length=500, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=150, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    listeners_count = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'estacion_radio'

    def __str__(self):
        return self.nombre

class Program(models.Model):
    nombre_programa = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    conductor = models.CharField(max_length=100, blank=True, null=True)
    dia_semana = models.IntegerField()  # 0=Domingo, 1=Lunes, etc.
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programacion'
        ordering = ['dia_semana', 'hora_inicio']

    def __str__(self):
        days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        day_name = days[self.dia_semana] if 0 <= self.dia_semana <= 6 else 'Desconocido'
        return f"{self.nombre_programa} - {day_name} {self.hora_inicio}"

class News(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    resumen = models.TextField(blank=True, null=True)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)
    autor_id = models.IntegerField(blank=True, null=True)
    autor_nombre = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    destacada = models.BooleanField(default=False)
    publicada = models.BooleanField(default=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'noticias'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo
