from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeterViewSet, MeterAssignmentViewSet, MeterDataViewSet, GenerateAlarmReport, GenerateMeterReport

# Router for admin-only endpoints
router = DefaultRouter()
router.register(r'meters', MeterViewSet)
router.register(r'meter-assignments', MeterAssignmentViewSet, basename='meter-assignments')
# Admin can still access these endpoints via the admin URL
router.register(r'meter-data', MeterDataViewSet, basename='meter-data')
router.register(r'meter-report', GenerateMeterReport, basename='meter-report')
router.register(r'meter-alarm-report', GenerateAlarmReport, basename='meter-alarm-report')

urlpatterns = [
    path('', include(router.urls)),
]
