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
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # Validate role
                role = serializer.validated_data.get('role')
                if role not in ['ADMIN', 'MANAGER', 'ENGINEER']:
                    return Response({
                        "error": "Invalid role",
                        "details": "Role must be ADMIN, MANAGER or ENGINEER."
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
                    "details": {
                        "message": f"{role} account created successfully",
                        "data": {
                            'user': UserSerializer(user).data,
                            'tokens': tokens
                        }
                    }
                }, status=status.HTTP_201_CREATED)
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": "Error creating user",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthViewSet(viewsets.ViewSet):
    def login(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)

                # Generate JWT tokens with custom claims
                tokens = get_tokens_for_user(user)

                return Response({
                    "details": {
                        "message": "Login successful",
                        "data": {
                            'user': UserSerializer(user).data,
                            'tokens': tokens
                        }
                    }
                })
            return Response({
                "error": "Authentication failed",
                "details": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({
                "error": "Error during login",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def logout(self, request):
        try:
            logout(request)
            return Response({
                "details": {
                    "message": "Logged out successfully"
                }
            })
        except Exception as e:
            return Response({
                "error": "Error during logout",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

