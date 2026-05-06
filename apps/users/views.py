from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserProfileUpdateSerializer,
    # UserRoleSerializer
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import UserRole

User = get_user_model()

from django.contrib.auth import login as django_login

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            user_data = UserSerializer(user).data
            response.data['user'] = user_data
        return response


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create default role
        UserRole.objects.create(user=user, role='client')

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Logout endpoint that blacklists the refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(generics.RetrieveUpdateAPIView):
    # ...
    authentication_classes = [SessionAuthentication, JWTAuthentication]   # allow both
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileUpdateSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer

    def get_object(self):
        print(f"Session user: {self.request.user} (authenticated: {self.request.user.is_authenticated})")
        return self.request.user


class UserDetailView(generics.RetrieveAPIView):
    """Get any user details (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class AssignRoleView(APIView):
    """Assign role to user (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            role = request.data.get('role')

            if role not in ['admin', 'staff', 'client', 'applicant']:
                return Response(
                    {"error": "Invalid role"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            UserRole.objects.get_or_create(user=user, role=role)
            return Response(
                {"message": f"Role '{role}' assigned to {user.email}"},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
