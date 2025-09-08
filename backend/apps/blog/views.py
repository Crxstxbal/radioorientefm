from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.utils.text import slugify
from .models import BlogPost, BlogComment
from .serializers import BlogPostSerializer, BlogCommentSerializer

class BlogPostListView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.filter(publicado=True)
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        titulo = serializer.validated_data['titulo']
        serializer.save(
            autor_id=self.request.user.id,
            autor_nombre=self.request.user.username
        )

class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.filter(publicado=True)
    serializer_class = BlogPostSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticatedOrReadOnly]

class BlogCommentListView(generics.ListCreateAPIView):
    serializer_class = BlogCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        articulo_id = self.kwargs['articulo_id']
        return BlogComment.objects.filter(
            articulo_id=articulo_id,
            aprobado=True
        )

    def perform_create(self, serializer):
        articulo_id = self.kwargs['articulo_id']
        serializer.save(
            articulo_id=articulo_id,
            autor_nombre=self.request.user.username,
            autor_correo=getattr(self.request.user, 'email', '')
        )
