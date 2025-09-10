from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatMessageListView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        sala = self.kwargs.get('sala', 'general')
        return ChatMessage.objects.filter(
            sala=sala
        ).order_by('-fecha_envio')[:50]

    def perform_create(self, serializer):
        sala = self.kwargs.get('sala', 'general')
        serializer.save(
            id_usuario=self.request.user.id,
            usuario_nombre=self.request.user.username,
            sala=sala
        )
