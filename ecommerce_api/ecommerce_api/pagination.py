from rest_framework.pagination import PageNumberPagination

class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for products.
    """
    page_size = 10  # Number of items per page
    page_size_query_param = 'page_size'  # Allows clients to override the page size using this query parameter
    max_page_size = 100  # Maximum number of items that can be requested per page