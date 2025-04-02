from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to create, update, and delete products.
    Read-only access is allowed for all users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'category__name'] # Enable search by name and category name

    # Implementation of filtering by category, price range, and stock availability.

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('q')
        if query:
            products = self.queryset.filter(
                Q(name__icontains=query) | Q(category__name__icontains=query)
            )
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        return Response({'message': 'Please provide a search query.'})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
