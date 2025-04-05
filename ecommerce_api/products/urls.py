from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, ReviewViewSet
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'orders', OrderViewSet, basename='order') # Register OrderViewSet
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'), # For user login and token generation
] + router.urls