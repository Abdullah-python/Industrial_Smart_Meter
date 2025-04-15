from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'meters', views.EngineersMeterViewSet, basename='meters')

urlpatterns = [
    path('engineer/', include(router.urls)),
]
