from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeterViewSet

router = DefaultRouter()
router.register(r'meters', MeterViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
