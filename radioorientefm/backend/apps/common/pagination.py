from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar para la mayoría de endpoints.

    Parámetros de query:
    - page: número de página (default: 1)
    - page_size: tamaño de página (default: 20, max: 100)

    Ejemplo de uso:
    /api/articulos/?page=2&page_size=10
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Respuesta personalizada con información adicional de paginación.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Paginación para conjuntos de datos grandes.
    Usada en endpoints administrativos o de reportes.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SmallResultsSetPagination(PageNumberPagination):
    """
    Paginación para listas pequeñas o destacadas.
    Usada para artículos destacados, programas del día, etc.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
