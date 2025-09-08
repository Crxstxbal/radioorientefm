from rest_framework import serializers
from .models import RadioStation, Program, News

class RadioStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadioStation
        fields = '__all__'

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'
        read_only_fields = ('autor_id',)
