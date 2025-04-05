from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserCreate, UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user') # Register UserViewSet

urlpatterns = [
    path('register/', UserCreate.as_view(), name='register'),
] + router.urls