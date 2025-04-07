from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer
from meter.models import Meter
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User

def get_tokens_for_user(user):
    """
    Generate JWT tokens with custom claims for a user
    """
    refresh = RefreshToken.for_user(user)

    # Add custom claims
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['role'] = user.role

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validate role
            role = serializer.validated_data.get('role')
            if role not in ['ADMIN', 'MANAGER', 'ENGINEER']:
                return Response({
                    'message': 'Invalid role. Role must be ADMIN, MANAGER or ENGINEER.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create user
            user = serializer.save()

            # For ADMIN role, set is_staff and is_superuser to True
            if role == 'ADMIN':
                user.is_staff = True
                user.is_superuser = True
                user.save()

            # Auto-login after signup
            login(request, user)

            # Generate JWT tokens with custom claims
            tokens = get_tokens_for_user(user)

            return Response({
                'message': f'{role} account created successfully',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AuthViewSet(viewsets.ViewSet):
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)

            # Generate JWT tokens with custom claims
            tokens = get_tokens_for_user(user)

            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': tokens
            })
        return Response({
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

    def logout(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})

