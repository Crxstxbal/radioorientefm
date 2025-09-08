from django.db import models

class BlogPost(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    resumen = models.TextField(blank=True, null=True)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)
    autor_id = models.IntegerField(blank=True, null=True)
    autor_nombre = models.CharField(max_length=100, blank=True, null=True)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, null=True, help_text="Tags separados por comas")
    publicado = models.BooleanField(default=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_articulos'
        ordering = ['-fecha_publicacion']

    def __str__(self):
        return self.titulo

class BlogComment(models.Model):
    articulo_id = models.IntegerField()
    autor_nombre = models.CharField(max_length=100)
    autor_correo = models.CharField(max_length=150, blank=True, null=True)
    contenido = models.TextField()
    aprobado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_comentarios'
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.autor_nombre} en artículo {self.articulo_id}"
