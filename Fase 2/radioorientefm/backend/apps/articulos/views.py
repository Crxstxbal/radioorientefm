from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.text import slugify
from apps.common.pagination import StandardResultsSetPagination, SmallResultsSetPagination
from .models import Categoria, Articulo
from .serializers import (
    CategoriaSerializer, ArticuloSerializer, ArticuloListSerializer,
    ArticuloCreateSerializer, BlogPostLegacySerializer
)

# ViewSets normalizados
class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para categorías (solo lectura)"""
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class ArticuloViewSet(viewsets.ModelViewSet):
    """ViewSet para artículos con soporte multimedia"""
    queryset = Articulo.objects.select_related('autor', 'categoria').filter(publicado=True)
    serializer_class = ArticuloSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticuloListSerializer
        elif self.action == 'create':
            return ArticuloCreateSerializer
        return ArticuloSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Incrementa vistas al obtener un artículo (solo una vez por usuario)"""
        instance = self.get_object()

        # Solo incrementar si el usuario está autenticado y no ha visto el artículo antes
        if request.user.is_authenticated:
            if not instance.usuarios_que_vieron.filter(id=request.user.id).exists():
                instance.usuarios_que_vieron.add(request.user)
                instance.vistas += 1
                instance.save(update_fields=['vistas'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def destacados(self, request):
        """Obtener artículos destacados (paginado)"""
        queryset = self.queryset.filter(destacado=True).order_by('-fecha_publicacion')

        # Usar paginación pequeña para destacados
        paginator = SmallResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ArticuloListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = ArticuloListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_categoria(self, request):
        """Obtener artículos por categoría (paginado)"""
        categoria_slug = request.query_params.get('categoria')
        if not categoria_slug:
            return Response([])

        queryset = self.queryset.filter(categoria__slug=categoria_slug)

        # Aplicar paginación
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ArticuloListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = ArticuloListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mas_vistos(self, request):
        """Obtener artículos más vistos (paginado)"""
        queryset = self.queryset.order_by('-vistas')

        # Usar paginación pequeña para más vistos
        paginator = SmallResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ArticuloListSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        serializer = ArticuloListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

# Views de compatibilidad para el frontend existente
class BlogPostListView(generics.ListCreateAPIView):
    """Vista de compatibilidad para artículos"""
    queryset = Articulo.objects.filter(publicado=True)
    serializer_class = BlogPostLegacySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Buscar o crear categoría por defecto
        categoria_default, created = Categoria.objects.get_or_create(
            nombre='General',
            defaults={'descripcion': 'Categoría general'}
        )
        serializer.save(
            autor=self.request.user,
            categoria=categoria_default
        )

class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista de compatibilidad para detalle de artículo"""
    queryset = Articulo.objects.filter(publicado=True)
    serializer_class = BlogPostLegacySerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticatedOrReadOnly]
