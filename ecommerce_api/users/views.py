# Create your views here.
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, permissions
from .serializers import UserSerializer

# For registration (public endpoint)
class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# For user management (admin only)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'put', 'delete', 'head', 'options']

    def get_queryset(self):
        # prevent non-admin users from listing all users
        if not self.request.user.is_staff:
            return User.objects.filter(pk=self.request.user.id)
        return User.objects.all()
