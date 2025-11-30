from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notificaciones', NotificationViewSet, basename='notificacion')

urlpatterns = [
    path('api/', include(router.urls)),
]
