from django.contrib.auth.models import User
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer

# Public endpoint for user registration
class UserCreate(generics.CreateAPIView):
    """
    Allows anyone to create a new user account.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# Admin-only endpoint for user management
class UserViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD operations for User objects.
    Accessible only to admin users.
    Non-admin users can only view and update their own profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'put', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Overrides the default queryset to restrict access for non-admin users.
        Admin users can list all users.
        Non-admin users can only access their own user object.
        """
        if not self.request.user.is_staff:
            return User.objects.filter(pk=self.request.user.id)
        return User.objects.all()

class CustomLogoutView(APIView):
    """
    Allows authenticated users (with TokenAuthentication) to logout by deleting their token.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Deletes the authentication token associated with the requesting user.
        Returns a success message or an error if no token is found.
        """
        try:
            request.user.auth_token.delete()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except (AttributeError, Token.DoesNotExist):
            return Response({'detail': 'No active token found.'}, status=status.HTTP_400_BAD_REQUEST)
        