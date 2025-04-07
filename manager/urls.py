from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'engineers', views.AssignedEngineerViewSet, basename='engineers')
urlpatterns = [
    path('manager/', include(router.urls)),
]
