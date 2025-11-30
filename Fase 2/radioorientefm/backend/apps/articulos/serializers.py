from rest_framework import serializers
from .models import Categoria, Articulo

class CategoriaSerializer(serializers.ModelSerializer):
    articulos_count = serializers.IntegerField(source='articulos.count', read_only=True)
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion', 'articulos_count']
        read_only_fields = ['slug']

class ArticuloSerializer(serializers.ModelSerializer):
    autor_nombre = serializers.CharField(source='autor.full_name', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen_destacada = serializers.SerializerMethodField()
    imagen_portada_url = serializers.SerializerMethodField()
    imagen_thumbnail_url = serializers.SerializerMethodField()
    archivo_adjunto_url = serializers.SerializerMethodField()
    tiene_multimedia = serializers.BooleanField(read_only=True)
    comentarios_count = serializers.IntegerField(source='comentarios.count', read_only=True)
    categoria_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'slug', 'contenido', 'resumen',
            'imagen_portada', 'imagen_portada_url', 'imagen_thumbnail', 'imagen_thumbnail_url',
            'imagen_url', 'imagen_destacada',
            'video_url', 'archivo_adjunto', 'archivo_adjunto_url',
            'autor', 'autor_nombre', 'categoria', 'categoria_nombre', 'categoria_detalle',
            'publicado', 'destacado', 'fecha_publicacion', 'fecha_creacion',
            'fecha_actualizacion', 'vistas', 'tiene_multimedia', 'comentarios_count'
        ]
        read_only_fields = ('slug', 'fecha_creacion', 'fecha_actualizacion', 'vistas')
    
    def get_imagen_destacada(self, obj):
        request = self.context.get('request')
        if obj.imagen_portada and request:
            return request.build_absolute_uri(obj.imagen_portada.url)
        return obj.imagen_url
    
    def get_imagen_portada_url(self, obj):
        request = self.context.get('request')
        if obj.imagen_portada and request:
            return request.build_absolute_uri(obj.imagen_portada.url)
        return None
    
    def get_imagen_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.imagen_thumbnail and request:
            return request.build_absolute_uri(obj.imagen_thumbnail.url)
        return None
    
    def get_archivo_adjunto_url(self, obj):
        request = self.context.get('request')
        if obj.archivo_adjunto and request:
            return request.build_absolute_uri(obj.archivo_adjunto.url)
        return None
    
    def get_categoria_detalle(self, obj):
        if obj.categoria:
            return {
                'id': obj.categoria.id,
                'nombre': obj.categoria.nombre
            }
        return None

class ArticuloListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    autor_nombre = serializers.CharField(source='autor.full_name', read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen_destacada = serializers.SerializerMethodField()
    imagen_portada = serializers.SerializerMethodField()
    imagen_thumbnail = serializers.SerializerMethodField()
    archivo_adjunto = serializers.SerializerMethodField()
    tiene_multimedia = serializers.BooleanField(read_only=True)
    categoria = serializers.SerializerMethodField()
    
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'slug', 'resumen', 'contenido',
            'imagen_portada', 'imagen_thumbnail', 'imagen_url', 'imagen_destacada',
            'video_url', 'archivo_adjunto',
            'autor_nombre', 'categoria', 'categoria_nombre', 
            'publicado', 'destacado',
            'fecha_publicacion', 'fecha_creacion', 'vistas', 'tiene_multimedia'
        ]
    
    def get_imagen_destacada(self, obj):
        request = self.context.get('request')
        if obj.imagen_portada and request:
            return request.build_absolute_uri(obj.imagen_portada.url)
        return obj.imagen_url
    
    def get_imagen_portada(self, obj):
        request = self.context.get('request')
        if obj.imagen_portada and request:
            return request.build_absolute_uri(obj.imagen_portada.url)
        return None
    
    def get_imagen_thumbnail(self, obj):
        request = self.context.get('request')
        if obj.imagen_thumbnail and request:
            return request.build_absolute_uri(obj.imagen_thumbnail.url)
        return None
    
    def get_archivo_adjunto(self, obj):
        request = self.context.get('request')
        if obj.archivo_adjunto and request:
            return request.build_absolute_uri(obj.archivo_adjunto.url)
        return None
    
    def get_categoria(self, obj):
        if obj.categoria:
            return {
                'id': obj.categoria.id,
                'nombre': obj.categoria.nombre
            }
        return None

class ArticuloCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear artículos"""
    
    class Meta:
        model = Articulo
        fields = [
            'titulo', 'contenido', 'resumen',
            'imagen_portada', 'imagen_url', 'video_url', 'archivo_adjunto',
            'categoria', 'publicado', 'destacado', 'fecha_publicacion'
        ]
    
    def create(self, validated_data):
        validated_data['autor'] = self.context['request'].user
        return super().create(validated_data)

# Serializers de compatibilidad para el frontend existente
class BlogPostLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    autor_id = serializers.IntegerField(source='autor.id', read_only=True)
    autor_nombre = serializers.CharField(source='autor.full_name', read_only=True)
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    imagen_destacada = serializers.SerializerMethodField()
    
    class Meta:
        model = Articulo
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'imagen_url', 'imagen_destacada',
            'autor_id', 'autor_nombre', 'categoria', 'publicado',
            'fecha_publicacion', 'fecha_creacion'
        ]
    
    def get_imagen_destacada(self, obj):
        request = self.context.get('request')
        if obj.imagen_portada and request:
            return request.build_absolute_uri(obj.imagen_portada.url)
        return obj.imagen_url
