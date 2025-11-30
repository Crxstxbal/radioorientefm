from django.db import models

class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        db_table = 'pais'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
    
    def __str__(self):
        return self.nombre

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='ciudades')
    
    class Meta:
        db_table = 'ciudad'
        unique_together = ['nombre', 'pais']
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'
    
    def __str__(self):
        return f"{self.nombre}, {self.pais.nombre}"

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='comunas')
    
    class Meta:
        db_table = 'comuna'
        unique_together = ['nombre', 'ciudad']
        verbose_name = 'Comuna'
        verbose_name_plural = 'Comunas'
    
    def __str__(self):
        return f"{self.nombre}, {self.ciudad.nombre}"
