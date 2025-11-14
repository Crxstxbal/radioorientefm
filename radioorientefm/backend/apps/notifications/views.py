# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet para notificaciones"""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer

    def get_queryset(self):
        """Solo notificaciones del usuario actual (staff y no-staff)"""
        user = self.request.user
        return self.queryset.filter(usuario=user)

    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Obtener notificaciones no leidas"""
        notificaciones = self.get_queryset().filter(leido=False)

        # Paginacion opcional
        page = self.paginate_queryset(notificaciones)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def contador(self, request):
        """Obtener contador de notificaciones no leidas"""
        count = self.get_queryset().filter(leido=False).count()
        return Response({'no_leidas': count})

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        """Marcar una notificacion como leida"""
        notificacion = self.get_object()
        notificacion.marcar_como_leido()
        serializer = self.get_serializer(notificacion)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las notificaciones como leidas"""
        count = self.get_queryset().filter(leido=False).update(leido=True)
        return Response({
            'message': f'{count} notificaciones marcadas como leidas',
            'count': count
        })

    @action(detail=True, methods=['delete'])
    def eliminar(self, request, pk=None):
        """Eliminar una notificacion"""
        notificacion = self.get_object()
        notificacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def eliminar_leidas(self, request):
        """Eliminar todas las notificaciones leidas"""
        count, _ = self.get_queryset().filter(leido=True).delete()
        return Response({
            'message': f'{count} notificaciones eliminadas',
            'count': count
        })

    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Filtrar notificaciones por tipo"""
        tipo = request.query_params.get('tipo')
        if not tipo:
            return Response({'error': 'Parametro "tipo" requerido'}, status=status.HTTP_400_BAD_REQUEST)

        notificaciones = self.get_queryset().filter(tipo=tipo)

        page = self.paginate_queryset(notificaciones)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notificaciones, many=True)
        return Response(serializer.data)
