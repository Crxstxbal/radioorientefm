from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegranteViewSet, BandaEmergenteViewSet, BandaEmergenteListCreateView

#router para los viewsets normalizados
router = DefaultRouter()
router.register(r'integrantes', IntegranteViewSet)
router.register(r'bandas', BandaEmergenteViewSet)

urlpatterns = [
    #apis normalizadas
    path('api/', include(router.urls)),
    #apis de compatibilidad para el frontend existente
    path('', BandaEmergenteListCreateView.as_view(), name='emergentes-list-create'),
]
