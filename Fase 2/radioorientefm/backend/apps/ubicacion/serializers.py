from rest_framework import serializers
from .models import Pais, Ciudad, Comuna

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ['id', 'nombre']

class CiudadSerializer(serializers.ModelSerializer):
    pais_nombre = serializers.CharField(source='pais.nombre', read_only=True)
    
    class Meta:
        model = Ciudad
        fields = ['id', 'nombre', 'pais', 'pais_nombre']

class ComunaSerializer(serializers.ModelSerializer):
    ciudad_nombre = serializers.CharField(source='ciudad.nombre', read_only=True)
    pais_nombre = serializers.CharField(source='ciudad.pais.nombre', read_only=True)
    
    class Meta:
        model = Comuna
        fields = ['id', 'nombre', 'ciudad', 'ciudad_nombre', 'pais_nombre']

class ComunaDetailSerializer(serializers.ModelSerializer):
    ciudad = CiudadSerializer(read_only=True)
    
    class Meta:
        model = Comuna
        fields = ['id', 'nombre', 'ciudad']
