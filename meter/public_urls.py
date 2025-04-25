from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeterDataViewSet, GenerateAlarmReport, GenerateMeterReport

# Router for public-accessible endpoints
router = DefaultRouter()
router.register(r'meter-data', MeterDataViewSet, basename='public-meter-data')
router.register(r'meter-report', GenerateMeterReport, basename='public-meter-report')
router.register(r'meter-alarm-report', GenerateAlarmReport, basename='public-meter-alarm-report')

urlpatterns = [
    path('', include(router.urls)),
]