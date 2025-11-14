from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaisViewSet, CiudadViewSet, ComunaViewSet

router = DefaultRouter()
router.register(r'paises', PaisViewSet)
router.register(r'ciudades', CiudadViewSet)
router.register(r'comunas', ComunaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
