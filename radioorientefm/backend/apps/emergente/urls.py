from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegranteViewSet, BandaEmergenteViewSet, BandaEmergenteListCreateView

# Router para los ViewSets normalizados
router = DefaultRouter()
router.register(r'integrantes', IntegranteViewSet)
router.register(r'bandas', BandaEmergenteViewSet)

urlpatterns = [
    # APIs normalizadas
    path('api/', include(router.urls)),
    # APIs de compatibilidad para el frontend existente
    path('', BandaEmergenteListCreateView.as_view(), name='emergentes-list-create'),
]
