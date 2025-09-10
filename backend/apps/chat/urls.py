from django.urls import path
from django.http import JsonResponse
from . import views

def chat_info(request):
    return JsonResponse({
        'message': 'Chat API',
        'endpoints': {
            'messages': '/api/chat/messages/',
            'messages_by_room': '/api/chat/messages/{room}/'
        }
    })

urlpatterns = [
    path('', chat_info, name='chat-info'),
    path('messages/', views.ChatMessageListView.as_view(), name='chat-messages'),
    path('messages/<str:sala>/', views.ChatMessageListView.as_view(), name='chat-messages-sala'),
]
