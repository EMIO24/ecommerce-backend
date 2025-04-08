from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product, Category, Order, Review
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer, ReviewSerializer
from ecommerce_api.pagination import ProductPagination  # Import the pagination class


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow admin users to perform create, update, and delete actions.
    Read-only access is granted to all other users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ProductFilter(FilterSet):
    """
    Filter set for the Product model, allowing filtering by category, price range, and stock availability.
    """
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    stock_available = django_filters.BooleanFilter(field_name='stock_quantity', lookup_expr='gt', method='filter_stock_available')

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max', 'stock_available']

    def filter_stock_available(self, queryset, name, value):
        """
        Filters the queryset to include only products with stock quantity greater than zero if value is True.
        """
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product objects.
    Provides CRUD operations with admin-only write access and read-only access for others.
    Supports filtering, searching, and pagination.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'category__name']  # Enable search by name and category name
    filterset_class = ProductFilter  # Use the ProductFilter
    pagination_class = ProductPagination  # Apply the pagination class

    @action(detail=False, methods=['GET'])
    def search(self, request):
        """
        Custom action to search products by name or category name.
        Applies pagination to the search results.
        """
        query = request.query_params.get('q')
        if query:
            products = self.queryset.filter(
                Q(name__icontains=query) | Q(category__name__icontains=query)
            )
            paginator = self.pagination_class()  # Apply pagination to search results
            page = paginator.paginate_queryset(products, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'message': 'Please provide a search query.'})


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Category objects.
    Provides standard CRUD operations.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Order objects.
    Authenticated users can create and view their own orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can place orders

    def get_queryset(self):
        """
        Returns only the orders associated with the currently authenticated user.
        """
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Saves the order, associating it with the currently authenticated user.
        """
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Review objects.
    Allows read access to all, and authenticated users can create reviews.
    Supports filtering reviews by product ID.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow reading by all, creating by authenticated
    queryset = Review.objects.all()

    def get_queryset(self):
        """
        Returns all reviews, or filters reviews by product ID if provided in the query parameters.
        """
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return super().get_queryset()

    def perform_create(self, serializer):
        """
        Saves the review, associating it with the currently authenticated user.
        """
        serializer.save(user=self.request.user)