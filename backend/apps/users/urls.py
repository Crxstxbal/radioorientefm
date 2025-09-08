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
            'update_profile': '/api/auth/profile/update/'
        }
    })

urlpatterns = [
    path('', auth_info, name='auth-info'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
