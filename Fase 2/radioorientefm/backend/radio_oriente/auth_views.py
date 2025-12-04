from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
# 1. CORRECCIÓN CLAVE: Importamos la utilidad para obtener TU usuario personalizado
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests

# 2. Obtenemos el modelo de usuario real (users.User) dinámicamente
# Esto soluciona el error "Manager isn't available... swapped for users.User"
User = get_user_model()

# ==============================================================================
# CONFIGURACIÓN
# Pega aquí el mismo CLIENT_ID que pusiste en el frontend (.env)
# Debe terminar en .apps.googleusercontent.com
# ==============================================================================
GOOGLE_CLIENT_ID = "463360249251-2lhvpjneamgtggoc3parp234qcpr2ep6.apps.googleusercontent.com"

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    """
    Recibe un ID Token de Google, lo verifica y devuelve un token de sesión de Django.
    """
    token_recibido = request.data.get('token')
    
    if not token_recibido:
        return Response({'error': 'No se proporcionó el token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 3. Verificar el token con los servidores de Google
        idinfo = id_token.verify_oauth2_token(
            token_recibido, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )

        # 4. Obtener información del usuario desde el token validado
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        
        if not idinfo.get('email_verified'):
             return Response({'error': 'El email no está verificado por Google'}, status=status.HTTP_400_BAD_REQUEST)

        # 5. Buscar usuario en Django o crearlo si no existe
        # Usamos filter().first() primero para ser compatibles con cualquier modelo de usuario
        user = User.objects.filter(email=email).first()

        if user:
            # Si existe, actualizamos nombre si falta
            if not user.first_name:
                user.first_name = first_name
                user.last_name = last_name
                user.save()
        else:
            # Si no existe, lo creamos. 
            # Usamos create_user que maneja el hasheo de contraseñas y campos obligatorios
            # Asumimos que el username será el email para evitar duplicados
            try:
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    first_name=first_name, 
                    last_name=last_name
                )
                # Establecemos una contraseña no utilizable ya que entra por Google
                user.set_unusable_password()
                user.save()
            except TypeError:
                # Fallback por si tu modelo 'users.User' no usa el campo 'username'
                user = User.objects.create_user(
                    email=email, 
                    first_name=first_name, 
                    last_name=last_name
                )
                user.set_unusable_password()
                user.save()

        # 6. Generar o recuperar el Token de autenticación de Django (DRF)
        token, _ = Token.objects.get_or_create(user=user)

        # 7. Responder al frontend con los datos de sesión
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': getattr(user, 'first_name', '') or getattr(user, 'username', email)
        }, status=status.HTTP_200_OK)

    except ValueError:
        return Response({'error': 'Token de Google inválido o expirado'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Imprimimos el error en la consola del servidor para depuración
        print(f"Error en Google Login: {str(e)}")
        return Response({'error': f"Error interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)