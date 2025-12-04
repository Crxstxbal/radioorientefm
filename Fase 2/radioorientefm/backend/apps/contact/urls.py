from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

#router para los viewsets normalizados
router = DefaultRouter()
router.register(r'tipos-asunto', views.TipoAsuntoViewSet)
router.register(r'estados', views.EstadoViewSet)
router.register(r'contactos', views.ContactoViewSet)
router.register(r'suscripciones', views.SuscripcionViewSet)

def contact_info(request):
    return JsonResponse({
        'message': 'Contact API',
        'endpoints': {
            'send_message': '/api/contact/message/',
            'subscribe': '/api/contact/subscribe/',
            'unsubscribe': '/api/contact/unsubscribe/'
        }
    })

urlpatterns = [
    path('', contact_info, name='contact-info'),
    #apis normalizadas
    path('api/', include(router.urls)),
    #apis de compatibilidad para el frontend existente
    path('message/', views.ContactMessageCreateView.as_view(), name='contact-message'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    #desuscripcion por token (desde email)
    path('unsubscribe-token/', views.unsubscribe_by_token, name='unsubscribe-by-token'),
]
