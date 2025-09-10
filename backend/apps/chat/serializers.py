from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'id_usuario', 'contenido', 'fecha_envio', 'usuario_nombre', 'tipo', 'sala']
        read_only_fields = ['id', 'fecha_envio']
