from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'assignments', views.UserAssignmentViewSet, basename='assignments')

urlpatterns = [
    path('', include(router.urls)),
    path('all-users/', views.UsersViewSet.as_view({'get': 'list'}), name='users'),

]
