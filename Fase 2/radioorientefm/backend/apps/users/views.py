from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserLegacySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
 #no usar ninguna autenticación para el registro
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
 #no usar ninguna autenticación para el login
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Inicio de sesión exitoso'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except:
        pass
    logout(request)
    return Response({'message': 'Sesión cerrada exitosamente'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#views de compatibilidad para el frontend existente
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_legacy(request):
    """endpoint de compatibilidad para el frontend existente"""
    serializer = UserLegacySerializer(request.user)
    return Response(serializer.data)

#views para recuperación de contraseña
@api_view(['POST'])
@permission_classes([AllowAny])
 #no usar ninguna autenticación para solicitar reseteo
def password_reset_request(request):
    """solicitar reseteo de contraseña. envía un correo electrónico con el enlace de recuperación. nota de seguridad: siempre retorna el mismo mensaje de éxito, independientemente de si el email existe o no, para prevenir user enumeration attacks"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)

            #generar token de reseteo
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            #construir url de reseteo (frontend)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            reset_url = f"{frontend_url}/resetear-contrasena/{uid}/{token}"

            #enviar correo electrónico
            subject = 'Recuperación de Contraseña - Radio Oriente FM'
            message = f"""hola {user.first_name or user.username}, recibimos una solicitud para restablecer tu contraseña en radio oriente fm. para crear una nueva contraseña, haz clic en el siguiente enlace: {reset_url} este enlace expirará en 24 horas. si no solicitaste este cambio, puedes ignorar este correo electrónico y tu contraseña permanecerá sin cambios. saludos, el equipo de radio oriente fm"""

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception:
                #fallar silenciosamente por seguridad
                pass

        except User.DoesNotExist:
            #no revelar si el email existe
            #no se envía correo, pero retornamos el mismo mensaje de éxito
            pass

        #siempre retornamos el mismo mensaje de éxito
        return Response({
            'message': 'Se ha enviado un correo electrónico con instrucciones para restablecer tu contraseña.'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
#no usar ninguna autenticación para confirmar reseteo
def password_reset_confirm(request):
    """confirmar reseteo de contraseña con token. establece la nueva contraseña"""
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']

        #establecer nueva contraseña
        user.set_password(new_password)
        user.save()

        return Response({
            'message': 'Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
