from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import BandaEmergente
from .serializers import BandaEmergenteSerializer

class BandaEmergenteListCreateView(generics.ListCreateAPIView):
    queryset = BandaEmergente.objects.all()
    serializer_class = BandaEmergenteSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(usuario=self.request.user)
        else:
            serializer.save()
