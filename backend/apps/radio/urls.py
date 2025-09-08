from django.urls import path
from django.http import JsonResponse
from . import views

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
    path('station/', views.RadioStationView.as_view(), name='radio-station'),
    path('programs/', views.ProgramListView.as_view(), name='program-list'),
    path('programs/<int:pk>/', views.ProgramDetailView.as_view(), name='program-detail'),
    path('news/', views.NewsListView.as_view(), name='news-list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news-detail'),
    path('update-song/', views.update_current_song, name='update-current-song'),
]
