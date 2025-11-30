from rest_framework import serializers
from .models import EstacionRadio, GeneroMusical, Conductor, Programa, ProgramaConductor, HorarioPrograma

class EstacionRadioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstacionRadio
        fields = '__all__'

class GeneroMusicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneroMusical
        fields = ['id', 'nombre', 'descripcion']

class ConductorSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Conductor (versión pública).
    """
    # Creamos un campo 'foto_url' que devuelva la URL completa de la imagen
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Conductor
        # Definimos los campos que queremos mostrar al público
        fields = [
            'id', 
            'nombre', 
            'apellido', 
            'apodo', 
            'foto_url'  # Usamos el campo personalizado
        ]

    def get_foto_url(self, obj):
        # Esta función construye la URL absoluta de la foto
        if obj.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto.url)
            # Fallback (aunque no debería pasar en una API)
            return obj.foto.url
        return None

class HorarioProgramaSerializer(serializers.ModelSerializer):
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    
    class Meta:
        model = HorarioPrograma
        fields = ['id', 'programa', 'dia_semana', 'dia_semana_display', 'hora_inicio', 'hora_fin', 'activo']

class ProgramaConductorSerializer(serializers.ModelSerializer):
    conductor_nombre = serializers.CharField(source='conductor.__str__', read_only=True)
    
    class Meta:
        model = ProgramaConductor
        fields = ['id', 'programa', 'conductor', 'conductor_nombre']

class ProgramaSerializer(serializers.ModelSerializer):
    conductores = ProgramaConductorSerializer(many=True, read_only=True)
    horarios = HorarioProgramaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Programa
        fields = ['id', 'nombre', 'descripcion', 'imagen_url', 'activo', 'conductores', 'horarios']

class ProgramaDetailSerializer(serializers.ModelSerializer):
    conductores = ConductorSerializer(source='conductores.conductor', many=True, read_only=True)
    horarios = HorarioProgramaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Programa
        fields = ['id', 'nombre', 'descripcion', 'imagen_url', 'activo', 'conductores', 'horarios']

# Serializers de compatibilidad para el frontend existente
class ProgramLegacySerializer(serializers.ModelSerializer):
    """Serializer para mantener compatibilidad con el frontend existente"""
    nombre_programa = serializers.CharField(source='nombre', read_only=True)
    conductor = serializers.SerializerMethodField()
    
    class Meta:
        model = Programa
        fields = ['id', 'nombre_programa', 'descripcion', 'conductor', 'activo']
    
    def get_conductor(self, obj):
        conductores = obj.conductores.all()
        if conductores:
            return ', '.join([str(pc.conductor) for pc in conductores])
        return None
