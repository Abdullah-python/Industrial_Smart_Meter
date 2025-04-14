from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'engineers', views.AssignedEngineerViewSet, basename='engineers')
router.register(r'meters', views.AssignedMetersViewSet, basename='meters')
router.register(r'assign-meter', views.AssignMeterToEngineerViewSet, basename='assign-meter')
urlpatterns = [
    path('manager/', include(router.urls)),
]
