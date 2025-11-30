from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from .models import TipoAsunto, Estado, Contacto, Suscripcion
from .serializers import (
    TipoAsuntoSerializer, EstadoSerializer, ContactoSerializer, ContactoCreateSerializer,
    SuscripcionSerializer, SuscripcionCreateSerializer, ContactMessageLegacySerializer,
    SubscriptionLegacySerializer
)

# ViewSets normalizados
class TipoAsuntoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para tipos de asunto (solo lectura)"""
    queryset = TipoAsunto.objects.all()
    serializer_class = TipoAsuntoSerializer
    permission_classes = [AllowAny]

class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para estados (solo lectura)"""
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """Obtener estados por tipo de entidad"""
        tipo = request.query_params.get('tipo')
        if tipo:
            estados = self.queryset.filter(tipo_entidad=tipo)
            serializer = self.get_serializer(estados, many=True)
            return Response(serializer.data)
        return Response([])

class ContactoViewSet(viewsets.ModelViewSet):
    """ViewSet para contactos"""
    queryset = Contacto.objects.select_related('tipo_asunto', 'estado', 'usuario').all()
    serializer_class = ContactoSerializer
    permission_classes = [AllowAny]
    # Solo usar TokenAuthentication, no SessionAuthentication para evitar CSRF en peticiones públicas
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContactoCreateSerializer
        return ContactoSerializer
    
    def get_queryset(self):
        # Los usuarios solo pueden ver sus propios contactos, excepto staff
        if self.request.user.is_staff:
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(usuario=self.request.user)
        else:
            # Para usuarios anónimos, devolver queryset vacío (solo pueden crear)
            return self.queryset.none()

class SuscripcionViewSet(viewsets.ModelViewSet):
    """ViewSet para suscripciones"""
    queryset = Suscripcion.objects.select_related('usuario').all()
    serializer_class = SuscripcionSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return SuscripcionCreateSerializer
        return SuscripcionSerializer

    def get_queryset(self):
        # Los usuarios solo pueden ver sus propias suscripciones, excepto staff
        if self.request.user.is_staff:
            return self.queryset
        elif self.request.user.is_authenticated:
            return self.queryset.filter(usuario=self.request.user)
        else:
            # Para usuarios anónimos, devolver queryset vacío (solo pueden crear)
            return self.queryset.none()

    def create(self, request, *args, **kwargs):
        """Override create para manejar mejor los errores de duplicados"""
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

            # Verificar si es una reactivación o una nueva suscripción
            suscripcion = serializer.instance
            email_existente = Suscripcion.objects.filter(
                email__iexact=request.data.get('email')
            ).exclude(id=suscripcion.id).exists()

            if email_existente:
                # Es una reactivación
                return Response(
                    {
                        'message': '¡Bienvenido de vuelta! Tu suscripción ha sido reactivada exitosamente.',
                        'email': suscripcion.email,
                        'reactivada': True
                    },
                    status=status.HTTP_200_OK,
                    headers=headers
                )
            else:
                # Es nueva suscripción
                return Response(
                    {
                        'message': '¡Suscripción exitosa! Recibirás un email de bienvenida pronto.',
                        'email': suscripcion.email,
                        'reactivada': False
                    },
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )

        except serializers.ValidationError as e:
            # Manejar errores de validación (email duplicado, etc)
            return Response(
                {
                    'error': e.detail if isinstance(e.detail, str) else e.detail,
                    'message': 'Ya estás suscrito a nuestro newsletter. ¡Gracias por tu interés!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Manejar otros errores inesperados
            return Response(
                {
                    'error': str(e),
                    'message': 'Ocurrió un error al procesar tu suscripción. Por favor, intenta nuevamente.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar suscripción"""
        suscripcion = self.get_object()
        suscripcion.activa = False
        suscripcion.fecha_baja = timezone.now()
        suscripcion.save()
        return Response({'message': 'Suscripción desactivada'})

# Views de compatibilidad para el frontend existente
class ContactMessageCreateView(generics.CreateAPIView):
    """Vista de compatibilidad para crear mensajes de contacto"""
    queryset = Contacto.objects.all()
    serializer_class = ContactMessageLegacySerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Crear usuario anónimo si no está autenticado
        if not self.request.user.is_authenticated:
            # Para el frontend existente, crear un contacto requiere autenticación
            # o implementar lógica para usuarios anónimos
            pass

@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe(request):
    """Endpoint de compatibilidad para suscripciones"""
    if not request.user.is_authenticated:
        return Response({'error': 'Autenticación requerida'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = SuscripcionCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        email = serializer.validated_data['email']
        suscripcion, created = Suscripcion.objects.get_or_create(
            email=email,
            defaults={
                'nombre': serializer.validated_data.get('nombre', ''),
                'usuario': request.user
            }
        )
        if created:
            return Response({'message': 'Suscripción exitosa'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Ya estás suscrito'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe(request):
    """Endpoint de compatibilidad para desuscripciones"""
    email = request.data.get('email')
    if email:
        try:
            suscripcion = Suscripcion.objects.get(email=email)
            suscripcion.activa = False
            suscripcion.save()
            return Response({'message': 'Desuscripción exitosa'})
        except Suscripcion.DoesNotExist:
            return Response({'error': 'Email no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def unsubscribe_by_token(request):
    """Cancelar suscripción usando token desde el email"""
    token = request.query_params.get('token')

    if not token:
        return render(request, 'emails/unsubscribe_result.html', {
            'success': False,
            'message': 'Token inválido o no proporcionado'
        })

    try:
        suscripcion = Suscripcion.objects.get(token_unsuscribe=token, activa=True)
        suscripcion.activa = False
        suscripcion.fecha_baja = timezone.now()
        suscripcion.save()

        return render(request, 'emails/unsubscribe_result.html', {
            'success': True,
            'message': 'Te has desuscrito exitosamente del newsletter de Radio Oriente',
            'email': suscripcion.email
        })
    except Suscripcion.DoesNotExist:
        return render(request, 'emails/unsubscribe_result.html', {
            'success': False,
            'message': 'Suscripción no encontrada o ya cancelada'
        })
