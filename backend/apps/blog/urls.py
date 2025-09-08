from django.urls import path
from django.http import JsonResponse
from . import views

def blog_info(request):
    return JsonResponse({
        'message': 'Blog API',
        'endpoints': {
            'posts': '/api/blog/posts/',
            'post_detail': '/api/blog/posts/{id}/',
            'comments': '/api/blog/posts/{id}/comments/'
        }
    })

urlpatterns = [
    path('', blog_info, name='blog-info'),
    path('posts/', views.BlogPostListView.as_view(), name='blog-posts'),
    path('posts/<int:pk>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
    path('posts/<int:articulo_id>/comments/', views.BlogCommentListView.as_view(), name='blog-comments'),
]
