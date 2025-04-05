from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
import django_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product, Category, Order, Review
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer, ReviewSerializer
from ecommerce_api.pagination import ProductPagination # Import the pagination class


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to create, update, and delete products.
    Read-only access is allowed for all users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ProductFilter(FilterSet):
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    stock_available = django_filters.BooleanFilter(field_name='stock_quantity', lookup_expr='gt', method='filter_stock_available')

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max', 'stock_available']

    def filter_stock_available(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'category__name'] # Enable search by name and category name
    filterset_class = ProductFilter # Use the ProductFilter
    pagination_class = ProductPagination # Apply the pagination class


    # Implementation of filtering by category, price range, and stock availability.

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('q')
        if query:
            products = self.queryset.filter(
                Q(name__icontains=query) | Q(category__name__icontains=query)
            )
            paginator = self.pagination_class() # Apply pagination to search results
            page = paginator.paginate_queryset(products, request)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'message': 'Please provide a search query.'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # Only logged-in users can place orders

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow reading by all, creating by authenticated

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id', None)
        if product_id:
            return Review.objects.filter(product_id=product_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)