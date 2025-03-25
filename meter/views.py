from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Meter
from .serializers import MeterSerializer

# Create your views here.

class MeterViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing meters.

    Available endpoints:
    - GET /api/meters/ - List all meters
    - POST /api/meters/ - Create a new meter
    - GET /api/meters/{device_id}/ - Get specific meter details by device_id
    - DELETE /api/meters/{device_id}/ - Delete a specific meter by device_id
    - PUT /api/meters/{device_id}/ - Update a meter by device_id
    - PATCH /api/meters/{device_id}/ - Partial update of a meter by device_id
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    lookup_field = 'device_id'

    def get_object(self):
        device_id = self.kwargs.get('device_id') or self.kwargs.get('pk')
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, device_id=device_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        """
        Get details of a specific meter by device_id
        URL: GET /api/meters/{device_id}/
        Example: GET /api/meters/METER001/
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create a new meter
        URL: POST /api/meters/
        Body: {
            "device_id": "your_device_id",
            "location": "your_location"
        }
        """
        print("Received POST request:", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific meter by device_id
        URL: DELETE /api/meters/{device_id}/
        Example: DELETE /api/meters/METER001/
        """
        instance = self.get_object()
        device_id = instance.device_id
        self.perform_destroy(instance)
        return Response(
            {"message": f"Meter with device ID '{device_id}' was successfully deleted"},
            status=status.HTTP_200_OK
        )
