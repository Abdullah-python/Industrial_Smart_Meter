from django.http import HttpResponseForbidden
from django.urls import resolve
from django.conf import settings
from accounts.models import User

class AdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define admin route prefixes that should be protected
        self.admin_prefixes = ['/admin/', '/api/admin/']  # Add more prefixes as needed

    def __call__(self, request):
        # Check if the current path starts with any admin prefix
        path = request.path_info
        is_admin_route = any(path.startswith(prefix) for prefix in self.admin_prefixes)

        if is_admin_route:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")

            # Check if user is admin or superuser
            if not (request.user.is_admin() or request.user.is_superuser):
                return HttpResponseForbidden("Admin privileges required")

        response = self.get_response(request)
        return response