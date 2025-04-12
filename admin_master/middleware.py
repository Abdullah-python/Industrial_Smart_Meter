from django.http import HttpResponseForbidden
from django.urls import resolve
from django.conf import settings
from accounts.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class AdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define admin route prefixes that should be protected
        self.admin_prefixes = ['/admin/', '/api/admin/']  # Add more prefixes as needed
        self.jwt_authentication = JWTAuthentication()

    def __call__(self, request):
        # Check if the current path starts with any admin prefix
        path = request.path_info
        is_admin_route = any(path.startswith(prefix) for prefix in self.admin_prefixes)

        if is_admin_route:
            print("is_admin_route", is_admin_route)
            # Check for Bearer token in Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return HttpResponseForbidden("Bearer token required")

            token = auth_header.split(' ')[1]

            try:
                # Validate the token
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = jwt_auth.get_user(validated_token)

                # Add user to request
                request.user = user  # Set the authenticated user
            except (InvalidToken, TokenError):
                return HttpResponseForbidden("Invalid token")

            # Check if user is admin or superuser
            if not (request.user.is_admin() or request.user.is_superuser):
                return HttpResponseForbidden("Admin privileges required")

        response = self.get_response(request)
        return response