from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Meter, MeterAssignment
from .serializers import MeterSerializer, MeterAssignmentSerializer
from accounts.models import User
from django.core.exceptions import ValidationError

class MeterViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing meters.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    lookup_field = 'device_id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("Received POST request:", request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        device_id = instance.device_id
        self.perform_destroy(instance)
        return Response(
            {"message": f"Meter with device ID '{device_id}' was successfully deleted"},
            status=status.HTTP_200_OK
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        """Custom perform_update method"""
        serializer.save()


class MeterAssignmentViewSet(viewsets.ViewSet):
    def list(self, request):
        assignments = MeterAssignment.objects.all()
        serializer = MeterAssignmentSerializer(assignments, many=True)
        return Response({
            "details": {
                "message": "Meter assignments retrieved successfully",
                "data": serializer.data
            }
        }, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = MeterAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                assignment = serializer.save()
                return Response({
                    "details": {
                        "message": "Meter assignment created successfully",
                        "data": MeterAssignmentSerializer(assignment).data
                    }
                }, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({
                    "error": "Validation error",
                    "details": e.message_dict if hasattr(e, 'message_dict') else {"detail": list(e)}
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    "error": "Error creating meter assignment",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                "error": "Validation failed",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


