from django.urls import re_path
from . import consumers

#permitir guiones y guiones bajos en el nombre de la sala
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[-\w]+)/$', consumers.ChatConsumer.as_asgi()),
]
