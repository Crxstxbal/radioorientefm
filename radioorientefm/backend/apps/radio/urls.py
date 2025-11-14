from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

# Router para los ViewSets normalizados
router = DefaultRouter()
router.register(r'estaciones', views.EstacionRadioViewSet)
router.register(r'generos', views.GeneroMusicalViewSet)
router.register(r'conductores', views.ConductorViewSet)
router.register(r'programas', views.ProgramaViewSet)
router.register(r'horarios', views.HorarioProgramaViewSet)

def radio_info(request):
    return JsonResponse({
        'message': 'Radio API',
        'endpoints': {
            'station': '/api/radio/station/',
            'programs': '/api/radio/programs/',
            'program_detail': '/api/radio/programs/{id}/',
            'news': '/api/radio/news/',
            'news_detail': '/api/radio/news/{id}/',
            'update_song': '/api/radio/update-song/'
        }
    })

urlpatterns = [
    path('', radio_info, name='radio-info'),
    # APIs normalizadas
    path('api/', include(router.urls)),
    # APIs de compatibilidad para el frontend existente
    path('station/', views.RadioStationView.as_view(), name='radio-station'),
    path('programs/', views.ProgramListView.as_view(), name='program-list'),
    path('programs/<int:pk>/', views.ProgramDetailView.as_view(), name='program-detail'),
    path('update-song/', views.update_current_song, name='update-current-song'),
    path('locutores/activos/', views.LocutoresActivosListView.as_view(), name='api_locutores_activos'),
    path('programas/', views.ProgramaListView.as_view(), name='api_programas_list'),
]
