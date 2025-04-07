from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'auth', views.AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
    # Add explicit routes for login and logout for clarity
    path('auth/login/', views.AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/logout/', views.AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    # JWT token refresh endpoint
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
