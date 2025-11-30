from django.urls import path
from django.http import JsonResponse
from . import views

def auth_info(request):
    return JsonResponse({
        'message': 'Authentication API',
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'logout': '/api/auth/logout/',
            'profile': '/api/auth/profile/',
            'update_profile': '/api/auth/profile/update/',
            'password_reset_request': '/api/auth/password-reset/',
            'password_reset_confirm': '/api/auth/password-reset-confirm/'
        }
    })

urlpatterns = [
    path('', auth_info, name='auth-info'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # Endpoints de compatibilidad
    path('profile/legacy/', views.profile_legacy, name='profile_legacy'),
    # Endpoints para recuperación de contraseña
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]
