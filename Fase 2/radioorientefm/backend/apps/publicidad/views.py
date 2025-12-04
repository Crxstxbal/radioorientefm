from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Publicidad, PublicidadWeb
from .serializers import (
    PublicidadSerializer, PublicidadCreateSerializer, PublicidadListSerializer,
    PublicidadWebSerializer
)

class PublicidadViewSet(viewsets.ModelViewSet):
    """viewset para publicidades"""
    queryset = Publicidad.objects.select_related('usuario').all()
    serializer_class = PublicidadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PublicidadListSerializer
        elif self.action == 'create':
            return PublicidadCreateSerializer
        return PublicidadSerializer
    
    def get_queryset(self):
        #los usuarios solo pueden ver sus propias publicidades, excepto staff
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """obtener publicidades activas"""
        activas = self.queryset.filter(activo=True)
        serializer = PublicidadListSerializer(activas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """obtener publicidades por tipo"""
        tipo = request.query_params.get('tipo')
        if tipo in ['WEB', 'RADIAL']:
            publicidades = self.queryset.filter(tipo=tipo)
            serializer = PublicidadListSerializer(publicidades, many=True)
            return Response(serializer.data)
        return Response([])
    
    @action(detail=False, methods=['get'])
    def web_activas(self, request):
        """obtener publicidades web activas para mostrar en el sitio"""
        from django.utils import timezone
        today = timezone.now().date()
        
        publicidades_web = self.queryset.filter(
            tipo='WEB',
            activo=True,
            fecha_inicio__lte=today,
            fecha_fin__gte=today
        ).select_related('web_config')
        
        serializer = PublicidadSerializer(publicidades_web, many=True)
        return Response(serializer.data)
