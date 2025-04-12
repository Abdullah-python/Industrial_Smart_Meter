from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeterViewSet, MeterAssignmentViewSet

router = DefaultRouter()
router.register(r'meters', MeterViewSet)
router.register(r'meter-assignments', MeterAssignmentViewSet, basename='meter-assignments')

urlpatterns = [
    path('', include(router.urls))
]
