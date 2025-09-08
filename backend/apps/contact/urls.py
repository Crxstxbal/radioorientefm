from django.urls import path
from django.http import JsonResponse
from . import views

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
    path('message/', views.ContactMessageCreateView.as_view(), name='contact-message'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
]
