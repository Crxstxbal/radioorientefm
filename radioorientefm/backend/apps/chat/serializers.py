from rest_framework import serializers
from .models import ChatMessage
from django.conf import settings
from django.apps import apps

class ChatMessageSerializer(serializers.ModelSerializer):
    usuario_bloqueado = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ['id', 'id_usuario', 'contenido', 'fecha_envio', 'usuario_nombre', 'tipo', 'sala', 'usuario_bloqueado']
        read_only_fields = ['id', 'fecha_envio', 'id_usuario', 'usuario_nombre', 'tipo', 'sala', 'usuario_bloqueado']

    def get_usuario_bloqueado(self, obj):
        try:
            UserModel = apps.get_model(settings.AUTH_USER_MODEL)
            user = UserModel.objects.get(id=obj.id_usuario)
            return user.chat_bloqueado
        except:
            return False
