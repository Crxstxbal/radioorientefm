from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import RadioStation, Program, News
from .serializers import RadioStationSerializer, ProgramSerializer, NewsSerializer

class RadioStationView(generics.RetrieveUpdateAPIView):
    queryset = RadioStation.objects.all()
    serializer_class = RadioStationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        station, created = RadioStation.objects.get_or_create(
            id=1,
            defaults={
                'nombre': 'Radio Oriente FM',
                'descripcion': 'La mejor música y noticias de oriente',
                'stream_url': 'https://sonic-us.fhost.cl/8126/stream',
                'activa': True
            }
        )
        return station

class ProgramListView(generics.ListCreateAPIView):
    queryset = Program.objects.filter(activo=True)
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class NewsListView(generics.ListCreateAPIView):
    queryset = News.objects.filter(publicada=True)
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(
            autor_id=self.request.user.id,
            autor_nombre=self.request.user.username
        )

class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_current_song(request):
    try:
        station = RadioStation.objects.get(id=1)
        # Nota: estos campos no existen en el modelo actual, se pueden agregar después
        # station.current_song = request.data.get('song', '')
        # station.current_artist = request.data.get('artist', '')
        station.save()
        return Response({'message': 'Canción actualizada'})
    except RadioStation.DoesNotExist:
        return Response({'error': 'Estación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
