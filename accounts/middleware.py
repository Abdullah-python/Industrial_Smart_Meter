from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from django.http import JsonResponse
from django.urls import resolve
from rest_framework_simplejwt.tokens import TokenError, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User

class CustomCSRFMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        # Skip CSRF check for exempt URLs
        if any(request.path.startswith(url) for url in settings.CSRF_EXEMPT_URLS):
            return None
        return super().process_view(request, callback, callback_args, callback_kwargs)

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # JWT protected paths
        self.protected_paths = [
            '/api/manager/',  # Protect the assignments endpoint
            '/api/engineer/',
            '/api/assignments/',
            '/api/all-users/',
        ]

        self.exempt_paths = [
            '/api/auth/',
        ]

    def __call__(self, request):
        current_path = request.path_info

        # Check if the current path is protected
        if any(current_path.startswith(path) for path in self.protected_paths):
            # Extract token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return JsonResponse({
                    "details": {
                        "message": "Authorization header must start with Bearer",
                        "data": None
                    }
                }, status=401)

            token = auth_header.split(' ')[1]

            try:
                # Decode and validate token
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)

                # Add user to request
                request.user = user

            except TokenError as e:
                return JsonResponse({
                    "details": {
                        "message": "Invalid or expired token",
                        "data": str(e)
                    }
                }, status=401)
            except User.DoesNotExist:
                return JsonResponse({
                    "details": {
                        "message": "User not found",
                        "data": None
                    }
                }, status=401)
            except Exception as e:
                return JsonResponse({
                    "details": {
                        "message": "Authentication error",
                        "data": str(e)
                    }
                }, status=401)

        response = self.get_response(request)
        return response