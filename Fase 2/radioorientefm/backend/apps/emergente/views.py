from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.common.pagination import StandardResultsSetPagination
from .models import Integrante, BandaEmergente, BandaLink, BandaIntegrante
from .serializers import (
    IntegranteSerializer, BandaEmergenteSerializer, BandaEmergenteCreateSerializer,
    BandaEmergenteListSerializer, BandaEmergentelLegacySerializer, BandaLinkSerializer
)

#viewsets normalizados
class IntegranteViewSet(viewsets.ModelViewSet):
    """viewset para integrantes"""
    queryset = Integrante.objects.all()
    serializer_class = IntegranteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class BandaEmergenteViewSet(viewsets.ModelViewSet):
    """viewset para bandas emergentes"""
    queryset = BandaEmergente.objects.select_related(
        'genero', 'estado', 'usuario', 'comuna__ciudad__pais'
    ).prefetch_related('links', 'integrantes').all()
    serializer_class = BandaEmergenteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BandaEmergenteListSerializer
        elif self.action == 'create':
            return BandaEmergenteCreateSerializer
        return BandaEmergenteSerializer
    
    def get_queryset(self):
        #los usuarios solo pueden ver sus propias bandas, excepto staff
        if self.request.user.is_staff:
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(usuario=self.request.user)
        else:
            #para usuarios anónimos, devolver queryset vacío
            return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """obtener bandas por estado (paginado)"""
        estado_id = request.query_params.get('estado_id')
        if not estado_id:
            return Response([])

        queryset = self.queryset.filter(estado_id=estado_id)

        #aplicar paginacion
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = BandaEmergenteListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = BandaEmergenteListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_genero(self, request):
        """obtener bandas por género (paginado)"""
        genero_id = request.query_params.get('genero_id')
        if not genero_id:
            return Response([])

        queryset = self.queryset.filter(genero_id=genero_id)

        #aplicar paginacion
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = BandaEmergenteListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = BandaEmergenteListSerializer(queryset, many=True)
        return Response(serializer.data)

#views de compatibilidad para el frontend existente
class BandaEmergenteListCreateView(generics.ListCreateAPIView):
    """vista de compatibilidad para bandas emergentes"""
    queryset = BandaEmergente.objects.all()
    serializer_class = BandaEmergentelLegacySerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            #buscar género por defecto
            from apps.radio.models import GeneroMusical
            genero_default, created = GeneroMusical.objects.get_or_create(
                nombre='Rock',
                defaults={'descripcion': 'Género rock'}
            )
            
            #buscar estado pendiente
            from apps.contact.models import Estado
            estado_pendiente = Estado.objects.filter(
                nombre__icontains='pendiente',
                tipo_entidad='banda'
            ).first()
            
            serializer.save(
                usuario=self.request.user,
                genero=genero_default,
                estado=estado_pendiente
            )
        else:
            serializer.save()
