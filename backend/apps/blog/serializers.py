from rest_framework import serializers
from .models import BlogPost, BlogComment

class BlogCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogComment
        fields = ['id', 'articulo_id', 'autor_nombre', 'autor_correo', 'contenido', 'aprobado', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'
        read_only_fields = ('autor_id', 'fecha_creacion', 'fecha_actualizacion')
