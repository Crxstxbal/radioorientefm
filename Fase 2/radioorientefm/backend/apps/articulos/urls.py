from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from . import views

#router para los viewsets normalizados
router = DefaultRouter()
router.register(r'categorias', views.CategoriaViewSet)
router.register(r'articulos', views.ArticuloViewSet)

def articulos_info(request):
    return JsonResponse({
        'message': 'Artículos API',
        'endpoints': {
            'articulos': '/api/articulos/articulos/',
            'articulo_detail': '/api/articulos/articulos/{slug}/',
            'categorias': '/api/articulos/categorias/',
            'destacados': '/api/articulos/articulos/destacados/',
            'por_categoria': '/api/articulos/articulos/por_categoria/?categoria={slug}',
            'mas_vistos': '/api/articulos/articulos/mas_vistos/',
            'comentarios': '/api/articulos/articulos/{slug}/comentarios/',
            'comentar': '/api/articulos/articulos/{slug}/comentar/',
            #endpoints legacy
            'posts_legacy': '/api/articulos/posts/',
            'post_detail_legacy': '/api/articulos/posts/{id}/',
        }
    })

urlpatterns = [
    path('', articulos_info, name='articulos-info'),
    #apis normalizadas
    path('api/', include(router.urls)),
    #apis de compatibilidad para el frontend existente
    path('posts/', views.BlogPostListView.as_view(), name='blog-posts'),
    path('posts/<int:pk>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
]
