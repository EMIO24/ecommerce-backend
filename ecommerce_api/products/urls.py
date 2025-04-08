from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, ReviewViewSet

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # For user login and token generation
] + router.urls