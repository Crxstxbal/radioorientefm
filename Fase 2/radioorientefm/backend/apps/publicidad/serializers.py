from rest_framework import serializers
from .models import (
    Publicidad, PublicidadWeb,
    UbicacionPublicidadWeb, SolicitudPublicidadWeb, ItemSolicitudWeb, ImagenPublicidadWeb
)

class PublicidadWebSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicidadWeb
        fields = ['id', 'url_destino', 'formato', 'impresiones', 'clics', 'archivo_media']

class PublicidadSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    web_config = PublicidadWebSerializer(read_only=True)
    
    class Meta:
        model = Publicidad
        fields = [
            'id', 'nombre_cliente', 'descripcion', 'tipo', 'tipo_display',
            'fecha_inicio', 'fecha_fin', 'activo', 'costo_total',
            'fecha_creacion', 'web_config'
        ]
        read_only_fields = ('fecha_creacion',)

class PublicidadCreateSerializer(serializers.ModelSerializer):
    """serializer para crear publicidades"""
    
    class Meta:
        model = Publicidad
        fields = [
            'nombre_cliente', 'descripcion', 'tipo', 'fecha_inicio', 'fecha_fin',
            'activo', 'costo_total'
        ]
    
    def create(self, validated_data):
        return super().create(validated_data)

class PublicidadListSerializer(serializers.ModelSerializer):
    """serializer simplificado para listas"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Publicidad
        fields = [
            'id', 'nombre_cliente', 'tipo', 'tipo_display', 'fecha_inicio',
            'fecha_fin', 'activo', 'costo_total'
        ]

#==========================
#serializers para modelos web
#==========================

class UbicacionPublicidadWebSerializer(serializers.ModelSerializer):
    """serializer para catálogo de ubicaciones"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = UbicacionPublicidadWeb
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'descripcion',
            'dimensiones', 'precio_mensual', 'activo', 'orden'
        ]
        read_only_fields = ('id',)

class ImagenPublicidadWebSerializer(serializers.ModelSerializer):
    """serializer para imágenes de publicidad"""
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ImagenPublicidadWeb
        fields = ['id', 'imagen', 'imagen_url', 'descripcion', 'orden', 'fecha_subida']
        read_only_fields = ('id', 'fecha_subida')
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None

class ItemSolicitudWebSerializer(serializers.ModelSerializer):
    """serializer para items de solicitud"""
    ubicacion_detalle = UbicacionPublicidadWebSerializer(source='ubicacion', read_only=True)
    imagenes = ImagenPublicidadWebSerializer(source='imagenes_web', many=True, read_only=True)
    
    class Meta:
        model = ItemSolicitudWeb
        fields = [
            'id', 'ubicacion', 'ubicacion_detalle', 'url_destino', 'formato',
            'precio_acordado', 'notas', 'imagenes'
        ]
        read_only_fields = ('id',)

class ItemSolicitudWebCreateSerializer(serializers.ModelSerializer):
    """serializer para crear items de solicitud"""
    
    class Meta:
        model = ItemSolicitudWeb
        fields = ['ubicacion', 'url_destino', 'formato', 'precio_acordado', 'notas']

class SolicitudPublicidadWebSerializer(serializers.ModelSerializer):
    """serializer completo para solicitudes"""
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    items_web = ItemSolicitudWebSerializer(many=True, read_only=True)
    publicacion_detalle = PublicidadSerializer(source='publicacion', read_only=True)
    
    class Meta:
        model = SolicitudPublicidadWeb
        fields = [
            'id', 'usuario', 'usuario_email', 'nombre_contacto', 'email_contacto',
            'telefono_contacto', 'preferencia_contacto', 'estado', 'estado_display',
            'fecha_solicitud', 'fecha_actualizacion', 'fecha_inicio_solicitada',
            'fecha_fin_solicitada', 'mensaje_usuario', 'notas_admin', 'motivo_rechazo',
            'costo_total_estimado', 'aprobado_por', 'fecha_aprobacion', 'publicacion',
            'publicacion_detalle', 'items_web'
        ]
        read_only_fields = (
            'id', 'usuario', 'fecha_solicitud', 'fecha_actualizacion',
            'estado', 'notas_admin', 'motivo_rechazo', 'costo_total_estimado',
            'aprobado_por', 'fecha_aprobacion', 'publicacion'
        )

class SolicitudPublicidadWebCreateSerializer(serializers.ModelSerializer):
    """serializer para crear solicitudes desde el frontend"""
    items_web = ItemSolicitudWebCreateSerializer(many=True)
    #alias de compatibilidad con clientes antiguos
    items = ItemSolicitudWebCreateSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = SolicitudPublicidadWeb
        fields = [
            'nombre_contacto', 'email_contacto', 'telefono_contacto',
            'preferencia_contacto', 'fecha_inicio_solicitada', 'fecha_fin_solicitada',
            'mensaje_usuario', 'items_web'
        ]
    
    def validate(self, data):
        """validar que haya al menos un item"""
        if not data.get('items_web') and not data.get('items'):
            raise serializers.ValidationError("Debe seleccionar al menos una ubicación")
        
        #validar fechas
        if data['fecha_fin_solicitada'] < data['fecha_inicio_solicitada']:
            raise serializers.ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio"
            )
        
        return data
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_web', None)
        if items_data is None:
            items_data = validated_data.pop('items', [])
        
        #asignar usuario autenticado
        validated_data['usuario'] = self.context['request'].user
        validated_data['estado'] = 'pendiente'
        
        #crear solicitud base
        solicitud = SolicitudPublicidadWeb.objects.create(**validated_data)
        
        #crear items y calcular costo total estimado (autocompletar precio si falta)
        costo_total = 0
        for item_data in items_data:
            precio = item_data.get('precio_acordado')
            if precio is None:
                ubicacion = item_data['ubicacion'] if isinstance(item_data['ubicacion'], UbicacionPublicidadWeb) else UbicacionPublicidadWeb.objects.get(id=item_data['ubicacion'].id if hasattr(item_data['ubicacion'], 'id') else item_data['ubicacion'])
                precio = ubicacion.precio_mensual
                item_data['precio_acordado'] = precio
            costo_total += precio
            ItemSolicitudWeb.objects.create(solicitud=solicitud, **item_data)
        #persistir costo total estimado en la solicitud creada
        solicitud.costo_total_estimado = costo_total
        solicitud.save(update_fields=['costo_total_estimado'])
        
        return solicitud

class SolicitudPublicidadWebListSerializer(serializers.ModelSerializer):
    """serializer simplificado para listar solicitudes"""
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudPublicidadWeb
        fields = [
            'id', 'nombre_contacto', 'estado', 'estado_display',
            'fecha_solicitud', 'fecha_inicio_solicitada', 'fecha_fin_solicitada',
            'costo_total_estimado', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items_web.count()
