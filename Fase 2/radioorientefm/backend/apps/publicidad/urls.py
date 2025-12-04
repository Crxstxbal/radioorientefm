from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    UbicacionPublicidadViewSet,
    SolicitudPublicidadViewSet,
    PublicidadWebCampaignViewSet,
)

#router para api rest
router = DefaultRouter()
router.register(r'ubicaciones', UbicacionPublicidadViewSet, basename='ubicacion')
router.register(r'solicitudes', SolicitudPublicidadViewSet, basename='solicitud')
router.register(r'campanias-web', PublicidadWebCampaignViewSet, basename='campanias-web')

urlpatterns = [
    path('api/', include(router.urls)),
]
