from rest_framework import serializers
from .models import BandaEmergente

class BandaEmergenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandaEmergente
        fields = '__all__'
        read_only_fields = ['id', 'fecha_envio', 'estado']
