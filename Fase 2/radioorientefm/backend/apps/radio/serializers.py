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
    """serializador para el modelo conductor (versión pública)"""
    #creamos un campo 'foto_url' que devuelva la url completa de la imagen
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Conductor
        #definimos los campos que queremos mostrar al publico
        fields = [
            'id', 
            'nombre', 
            'apellido', 
            'apodo', 
            'foto_url'  # Usamos el campo personalizado
        ]

    def get_foto_url(self, obj):
        #esta funcion construye la url absoluta de la foto
        if obj.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto.url)
            #fallback (aunque no debería pasar en una api)
            return obj.foto.url
        return None

class HorarioProgramaSerializer(serializers.ModelSerializer):
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    
    class Meta:
        model = HorarioPrograma
        fields = ['id', 'programa', 'dia_semana', 'dia_semana_display', 'hora_inicio', 'hora_fin', 'activo']

class ProgramaConductorSerializer(serializers.ModelSerializer):
    conductor_nombre = serializers.CharField(source='conductor.__str__', read_only=True)
    conductor_foto = serializers.SerializerMethodField()
    conductor_apodo = serializers.CharField(source='conductor.apodo', read_only=True)

    class Meta:
        model = ProgramaConductor
        fields = ['id', 'programa', 'conductor', 'conductor_nombre', 'conductor_foto', 'conductor_apodo']

    def get_conductor_foto(self, obj):
        if obj.conductor and obj.conductor.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.conductor.foto.url)
            return obj.conductor.foto.url
        return None

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

#serializers de compatibilidad para el frontend existente
class ProgramLegacySerializer(serializers.ModelSerializer):
    """serializer para mantener compatibilidad con el frontend existente"""
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
