from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ChatMessage, ContentFilterConfig, PalabraProhibida, InfraccionUsuario
from .serializers import ChatMessageSerializer
from apps.radio.models import EstacionRadio
from .utils import content_analyzer

class ChatMessageListView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
  #desactivar paginación - se maneja en el frontend

    def get_queryset(self):
        sala = self.kwargs.get('sala', 'radio-oriente')
        return ChatMessage.objects.filter(
            sala=sala
        ).order_by('-fecha_envio')[:200]

    def perform_create(self, serializer):
        #verificar si el usuario está bloqueado
        if self.request.user.chat_bloqueado:
            raise ValidationError({'detail': 'Has sido bloqueado del chat. Contacta con un administrador.'})

        #verificar si la radio está online
        try:
            radio = EstacionRadio.objects.first()
            if not radio or not radio.activo:
                raise ValidationError({'detail': 'El chat solo está disponible cuando la radio está en vivo'})
        except EstacionRadio.DoesNotExist:
            raise ValidationError({'detail': 'No se pudo verificar el estado de la radio'})

        #analizar contenido con machine learning
        contenido = serializer.validated_data.get('contenido', '')
        analysis = content_analyzer.analyze_message(
            contenido=contenido,
            id_usuario=self.request.user.id,
            usuario_nombre=self.request.user.username
        )

        #si el mensaje no está permitido, bloquear
        if not analysis['allowed']:
            #si fue auto-bloqueado, actualizar el estado del usuario
            if analysis.get('auto_blocked'):
                self.request.user.chat_bloqueado = True
                self.request.user.save()

            raise ValidationError({
                'detail': analysis['reason'],
                'toxicity_score': analysis['score'],
                'infraction_type': analysis['infraction_type']
            })

        #si hay advertencia, incluirla en la respuesta
        warning = analysis.get('warning')

        sala = self.kwargs.get('sala', 'radio-oriente')
        serializer.save(
            usuario=self.request.user,
            usuario_nombre=self.request.user.username,
            sala=sala,
            tipo='user'
        )

        #agregar advertencia al contexto si existe
        if warning:
            self.warning_message = warning

class ChatMessageDeleteView(generics.DestroyAPIView):
    """vista para que los administradores eliminen mensajes del chat"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    queryset = ChatMessage.objects.all()

class RadioStatusView(APIView):
    """vista para verificar si la radio está online"""
    permission_classes = []

    def get(self, request):
        try:
            radio = EstacionRadio.objects.first()
            return Response({
                'is_online': radio.activo if radio else False,
                'listeners_count': radio.listeners_count if radio else 0
            })
        except EstacionRadio.DoesNotExist:
            return Response({
                'is_online': False,
                'listeners_count': 0
            })

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def toggle_user_block(request, user_id):
    """bloquear o desbloquear usuario del chat"""
    try:
        User = settings.AUTH_USER_MODEL
        from django.apps import apps
        UserModel = apps.get_model(User)
        user = get_object_or_404(UserModel, id=user_id)

        user.chat_bloqueado = not user.chat_bloqueado
        user.save()

        return Response({
            'success': True,
            'bloqueado': user.chat_bloqueado,
            'message': f'Usuario {"bloqueado" if user.chat_bloqueado else "desbloqueado"} correctamente'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

class ClearAllMessagesView(generics.GenericAPIView):
    """vista para limpiar todos los mensajes del chat"""
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def post(self, request, *args, **kwargs):
        print(f"=== CLEAR ALL MESSAGES ===")
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is staff: {request.user.is_staff if request.user.is_authenticated else 'N/A'}")

        try:
            #obtener sala del request
            sala = request.data.get('sala', 'radio-oriente') if request.data else 'radio-oriente'
            print(f"Eliminando mensajes de sala: {sala}")

            deleted_count = ChatMessage.objects.filter(sala=sala).delete()[0]
            print(f"Mensajes eliminados: {deleted_count}")

            return Response({
                'success': True,
                'deleted_count': deleted_count,
                'message': f'Se eliminaron {deleted_count} mensajes correctamente'
            })
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"ERROR en clear_all_messages: {str(e)}")
            print(error_trace)
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


#============== filtro de contenido ml ==============

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def manage_filter_config(request):
    """obtener o actualizar configuracion del filtro ml"""
    config = ContentFilterConfig.get_config()

    if request.method == 'GET':
        return Response({
            'activo': config.activo,
            'umbral_toxicidad': config.umbral_toxicidad,
            'bloquear_enlaces': config.bloquear_enlaces,
            'modo_accion': config.modo_accion,
            'strikes_para_bloqueo': config.strikes_para_bloqueo,
        })

    elif request.method == 'POST':
        try:
            config.activo = request.data.get('activo', config.activo)
            config.umbral_toxicidad = float(request.data.get('umbral_toxicidad', config.umbral_toxicidad))
            config.bloquear_enlaces = request.data.get('bloquear_enlaces', config.bloquear_enlaces)
            config.modo_accion = request.data.get('modo_accion', config.modo_accion)
            config.strikes_para_bloqueo = int(request.data.get('strikes_para_bloqueo', config.strikes_para_bloqueo))
            config.save()

            return Response({
                'success': True,
                'message': 'Configuración actualizada correctamente',
                'config': {
                    'activo': config.activo,
                    'umbral_toxicidad': config.umbral_toxicidad,
                    'bloquear_enlaces': config.bloquear_enlaces,
                    'modo_accion': config.modo_accion,
                    'strikes_para_bloqueo': config.strikes_para_bloqueo,
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def manage_prohibited_words(request):
    """gestionar palabras prohibidas"""

    if request.method == 'GET':
        palabras = PalabraProhibida.objects.all().order_by('palabra')
        return Response({
            'palabras': [{
                'id': p.id,
                'palabra': p.palabra,
                'severidad': p.severidad,
                'activa': p.activa
            } for p in palabras]
        })

    elif request.method == 'POST':
        try:
            palabra = request.data.get('palabra', '').strip().lower()
            severidad = request.data.get('severidad', 'media')

            if not palabra:
                return Response({
                    'success': False,
                    'message': 'Debes proporcionar una palabra'
                }, status=status.HTTP_400_BAD_REQUEST)

            #verificar si ya existe
            if PalabraProhibida.objects.filter(palabra=palabra).exists():
                return Response({
                    'success': False,
                    'message': 'Esta palabra ya está en la lista'
                }, status=status.HTTP_400_BAD_REQUEST)

            nueva_palabra = PalabraProhibida.objects.create(
                palabra=palabra,
                severidad=severidad
            )

            return Response({
                'success': True,
                'message': 'Palabra agregada correctamente',
                'palabra': {
                    'id': nueva_palabra.id,
                    'palabra': nueva_palabra.palabra,
                    'severidad': nueva_palabra.severidad,
                    'activa': nueva_palabra.activa
                }
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            palabra_id = request.data.get('id')
            palabra = get_object_or_404(PalabraProhibida, id=palabra_id)
            palabra.delete()

            return Response({
                'success': True,
                'message': 'Palabra eliminada correctamente'
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def get_infractions(request):
    """obtener lista de infracciones registradas"""
    infracciones = InfraccionUsuario.objects.all().order_by('-fecha_infraccion')[:100]

    return Response({
        'infracciones': [{
            'id': i.id,
            'id_usuario': i.id_usuario,
            'usuario_nombre': i.usuario_nombre,
            'mensaje_original': i.mensaje_original,
            'tipo_infraccion': i.tipo_infraccion,
            'score_toxicidad': i.score_toxicidad,
            'fecha_infraccion': i.fecha_infraccion.isoformat(),
            'accion_tomada': i.accion_tomada
        } for i in infracciones]
    })


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAdminUser])
def get_blocked_users(request):
    """obtener lista de todos los usuarios bloqueados del chat"""
    try:
        User = settings.AUTH_USER_MODEL
        from django.apps import apps
        UserModel = apps.get_model(User)

        #obtener todos los usuarios bloqueados
        blocked_users = UserModel.objects.filter(chat_bloqueado=True).order_by('username')

        #para cada usuario, contar sus infracciones
        users_data = []
        for user in blocked_users:
            infracciones_count = InfraccionUsuario.objects.filter(usuario_id=user.id).count()

            #obtener ultima infracción
            ultima_infraccion = InfraccionUsuario.objects.filter(
                usuario_id=user.id
            ).order_by('-fecha_infraccion').first()

            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'infracciones_count': infracciones_count,
                'ultima_infraccion': {
                    'tipo': ultima_infraccion.tipo_infraccion,
                    'fecha': ultima_infraccion.fecha_infraccion.isoformat(),
                    'score': ultima_infraccion.score_toxicidad
                } if ultima_infraccion else None
            })

        return Response({
            'usuarios_bloqueados': users_data,
            'total': len(users_data)
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
