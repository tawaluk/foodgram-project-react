from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Паджинатор для проекта фудграм."""

    page_size_query_param = 'limit'
