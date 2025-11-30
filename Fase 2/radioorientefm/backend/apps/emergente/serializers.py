from rest_framework import serializers
from .models import Integrante, BandaEmergente, BandaLink, BandaIntegrante

class IntegranteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Integrante
        fields = ['id', 'nombre']

class BandaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandaLink
        fields = ['id', 'tipo', 'url']

class BandaIntegranteSerializer(serializers.ModelSerializer):
    integrante_nombre = serializers.CharField(source='integrante.nombre', read_only=True)
    
    class Meta:
        model = BandaIntegrante
        fields = ['id', 'integrante', 'integrante_nombre']

class BandaEmergenteSerializer(serializers.ModelSerializer):
    genero_nombre = serializers.CharField(source='genero.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.full_name', read_only=True)
    comuna_nombre = serializers.CharField(source='comuna.nombre', read_only=True)
    ciudad_nombre = serializers.CharField(source='comuna.ciudad.nombre', read_only=True)
    pais_nombre = serializers.CharField(source='comuna.ciudad.pais.nombre', read_only=True)
    revisado_por_nombre = serializers.CharField(source='revisado_por.full_name', read_only=True)
    
    # Relaciones anidadas
    links = BandaLinkSerializer(many=True, read_only=True)
    integrantes = BandaIntegranteSerializer(many=True, read_only=True)
    
    class Meta:
        model = BandaEmergente
        fields = [
            'id', 'nombre_banda', 'email_contacto', 'telefono_contacto', 'mensaje',
            'documento_presentacion', 'genero', 'genero_nombre', 'usuario', 'usuario_nombre',
            'estado', 'estado_nombre', 'comuna', 'comuna_nombre', 'ciudad_nombre', 'pais_nombre',
            'fecha_envio', 'fecha_revision', 'revisado_por', 'revisado_por_nombre',
            'links', 'integrantes'
        ]
        read_only_fields = ('fecha_envio', 'fecha_revision', 'revisado_por')

class BandaEmergenteCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear bandas emergentes"""
    links_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    integrantes_data = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = BandaEmergente
        fields = [
            'nombre_banda', 'email_contacto', 'telefono_contacto', 'mensaje',
            'documento_presentacion', 'genero', 'comuna', 'links_data', 'integrantes_data'
        ]
    
    def create(self, validated_data):
        links_data = validated_data.pop('links_data', [])
        integrantes_data = validated_data.pop('integrantes_data', [])
        
        # Asignar usuario actual y estado por defecto
        validated_data['usuario'] = self.context['request'].user
        
        # Buscar primer estado disponible para bandas
        from apps.contact.models import Estado
        estado_inicial = Estado.objects.filter(
            tipo_entidad='banda'
        ).first()  # Toma el primer estado disponible (Recibida)
        if estado_inicial:
            validated_data['estado'] = estado_inicial
        
        banda = super().create(validated_data)
        
        # Crear links
        for link_data in links_data:
            BandaLink.objects.create(banda=banda, **link_data)
        
        # Crear integrantes
        for integrante_nombre in integrantes_data:
            integrante, created = Integrante.objects.get_or_create(nombre=integrante_nombre)
            BandaIntegrante.objects.create(banda=banda, integrante=integrante)
        
        return banda

class BandaEmergenteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    genero_nombre = serializers.CharField(source='genero.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='estado.nombre', read_only=True)
    
    class Meta:
        model = BandaEmergente
        fields = [
            'id', 'nombre_banda', 'genero_nombre', 'estado_nombre',
            'fecha_envio', 'email_contacto'
        ]

# Serializers de compatibilidad para el frontend existente
class BandaEmergentelLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    genero = serializers.CharField(source='genero.nombre', read_only=True)
    ciudad = serializers.CharField(source='comuna.ciudad.nombre', read_only=True)
    estado = serializers.CharField(source='estado.nombre', read_only=True)
    correo_contacto = serializers.CharField(source='email_contacto', read_only=True)
    integrantes = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    
    class Meta:
        model = BandaEmergente
        fields = [
            'id', 'nombre_banda', 'integrantes', 'genero', 'ciudad',
            'correo_contacto', 'telefono_contacto', 'mensaje', 'links',
            'fecha_envio', 'estado'
        ]
    
    def get_integrantes(self, obj):
        return ', '.join([bi.integrante.nombre for bi in obj.integrantes.all()])
    
    def get_links(self, obj):
        return '\n'.join([f"{link.tipo}: {link.url}" for link in obj.links.all()])
