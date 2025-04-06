from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import views as auth_views # Import Django's auth views
from .views import UserCreate, UserViewSet, CustomLogoutView # Import your custom logout view

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', UserCreate.as_view(), name='register'),
    path('login/', ObtainAuthToken.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'), # Use your custom view
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'), # Add password reset URLs
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] + router.urls 