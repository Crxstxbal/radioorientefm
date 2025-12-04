#api views para publicidad
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.utils import timezone

from ..models import (
    Publicidad,
    PublicidadWeb,
    UbicacionPublicidadWeb,
    SolicitudPublicidadWeb,
    ItemSolicitudWeb,
    ImagenPublicidadWeb,
)
from ..serializers import (
    PublicidadSerializer,
    UbicacionPublicidadWebSerializer,
    SolicitudPublicidadWebSerializer,
    SolicitudPublicidadWebCreateSerializer,
    SolicitudPublicidadWebListSerializer,
    ImagenPublicidadWebSerializer,
)


class UbicacionPublicidadViewSet(viewsets.ReadOnlyModelViewSet):
    """viewset para catálogo de ubicaciones de publicidad. solo lectura - las ubicaciones se gestionan desde el admin"""
    queryset = UbicacionPublicidadWeb.objects.filter(activo=True)
    serializer_class = UbicacionPublicidadWebSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """retornar solo ubicaciones activas ordenadas"""
        return UbicacionPublicidadWeb.objects.filter(activo=True).order_by('orden', 'nombre')


class SolicitudPublicidadViewSet(viewsets.ModelViewSet):
    """viewset para gestion de solicitudes de publicidad. - list: ver mis solicitudes - create: crear nueva solicitud - retrieve: ver detalle de una solicitud - update/partial_update: actualizar solicitud (solo si está pendiente)"""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_queryset(self):
        """cada usuario solo ve sus propias solicitudes"""
        return SolicitudPublicidadWeb.objects.filter(usuario=self.request.user).prefetch_related(
            'items_web__ubicacion', 'items_web__imagenes_web'
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SolicitudPublicidadWebCreateSerializer
        elif self.action == 'list':
            return SolicitudPublicidadWebListSerializer
        return SolicitudPublicidadWebSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """crear nueva solicitud de publicidad"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        
        #retornar con serializer completo
        output_serializer = SolicitudPublicidadWebSerializer(solicitud)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """solo permitir actualización si está pendiente"""
        instance = self.get_object()
        if instance.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden modificar solicitudes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], parser_classes=[JSONParser])
    @transaction.atomic
    def aprobar(self, request, pk=None):
        """aprobar y publicar una solicitud web creando publicidad + publicidadweb"""
        solicitud = self.get_object()
        if solicitud.estado not in ['pendiente', 'en_revision']:
            return Response({'error': 'La solicitud no está pendiente/en revisión'}, status=status.HTTP_400_BAD_REQUEST)
        if solicitud.publicacion_id:
            return Response({'error': 'La solicitud ya tiene una campaña publicada'}, status=status.HTTP_400_BAD_REQUEST)

        items = list(solicitud.items_web.select_related('ubicacion'))
        if not items:
            return Response({'error': 'La solicitud no tiene ítems'}, status=status.HTTP_400_BAD_REQUEST)

        #calcular costo total desde los ítems
        costo_total = sum([i.precio_acordado for i in items])

        #definir rango a partir de la aprobación
        from datetime import timedelta
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        #crear publicidad base
        pub = Publicidad.objects.create(
            nombre_cliente=solicitud.nombre_contacto or solicitud.usuario.email,
            descripcion=solicitud.mensaje_usuario,
            tipo='WEB',
            fecha_inicio=start_date,
            fecha_fin=end_date,
            activo=True,
            costo_total=costo_total,
        )

        #tomar ítem principal (primero) para configurar publicidadweb
        principal = items[0]
        PublicidadWeb.objects.create(
            publicidad=pub,
            url_destino=principal.url_destino,
            formato=principal.formato,
            impresiones=0,
            clics=0,
            archivo_media=None,
        )

        #actualizar solicitud como aprobada y enlazar publicacion
        solicitud.estado = 'aprobada'
        solicitud.aprobado_por = request.user
        solicitud.fecha_aprobacion = timezone.now()
        solicitud.publicacion = pub
        #actualizar fechas solicitadas para reflejar el rango real
        try:
            solicitud.fecha_inicio_solicitada = start_date
            solicitud.fecha_fin_solicitada = end_date
            solicitud.save(update_fields=['estado', 'aprobado_por', 'fecha_aprobacion', 'publicacion', 'fecha_inicio_solicitada', 'fecha_fin_solicitada'])
        except Exception:
            solicitud.save(update_fields=['estado', 'aprobado_por', 'fecha_aprobacion', 'publicacion'])

        return Response(SolicitudPublicidadWebSerializer(solicitud).data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def subir_imagen(self, request, pk=None):
        """subir imagen para un item especifico de la solicitud. requiere: item_id, imagen, descripcion (opcional), orden (opcional)"""
        solicitud = self.get_object()
        
        #validar que la solicitud esté pendiente
        if solicitud.estado not in ['pendiente', 'en_revision']:
            return Response(
                {'error': 'No se pueden agregar imágenes a solicitudes aprobadas/rechazadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item_id = request.data.get('item_id')
        if not item_id:
            return Response(
                {'error': 'Se requiere item_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = solicitud.items_web.get(id=item_id)
        except ItemSolicitudWeb.DoesNotExist:
            return Response(
                {'error': 'Item no encontrado en esta solicitud'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        #crear imagen
        imagen_data = {
            'item': item.id,
            'imagen': request.data.get('imagen'),
            'descripcion': request.data.get('descripcion', ''),
            'orden': request.data.get('orden', 0)
        }
        
        serializer = ImagenPublicidadWebSerializer(data=imagen_data, context={'request': request})
        if serializer.is_valid():
            serializer.save(item=item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def eliminar_imagen(self, request, pk=None):
        """eliminar una imagen de un item. requiere: imagen_id"""
        solicitud = self.get_object()
        
        if solicitud.estado not in ['pendiente', 'en_revision']:
            return Response(
                {'error': 'No se pueden eliminar imágenes de solicitudes aprobadas/rechazadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        imagen_id = request.data.get('imagen_id')
        if not imagen_id:
            return Response(
                {'error': 'Se requiere imagen_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            imagen = ImagenPublicidadWeb.objects.get(
                id=imagen_id,
                item__solicitud=solicitud
            )
            imagen.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ImagenPublicidadWeb.DoesNotExist:
            return Response(
                {'error': 'Imagen no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        """endpoint alternativo para obtener solicitudes del usuario actual"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = SolicitudPublicidadWebListSerializer(queryset, many=True)
        return Response(serializer.data)


class PublicidadWebCampaignViewSet(viewsets.ModelViewSet):
    """administración de campañas publicadas web desde el dashboard"""
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    serializer_class = PublicidadSerializer

    def get_queryset(self):
        return Publicidad.objects.filter(tipo='WEB').select_related('web_config')

    @action(detail=True, methods=['patch'], parser_classes=[JSONParser])
    def actualizar_web(self, request, pk=None):
        """actualizar campos especificos de la config web (url_destino, formato, archivo_media)"""
        pub = self.get_object()
        config = getattr(pub, 'web_config', None)
        if not config:
            return Response({'error': 'La campaña no tiene configuración web'}, status=status.HTTP_400_BAD_REQUEST)

        for campo in ['url_destino', 'formato', 'archivo_media']:
            if campo in request.data:
                setattr(config, campo, request.data[campo])
        config.save()
        return Response(PublicidadSerializer(pub).data)
