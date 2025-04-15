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
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "details": {
                    "message": "Meter retrieved successfully",
                    "data": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "error": "Error retrieving meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            print("Received POST request:", request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "details": {
                    "message": "Meter created successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": "Error creating meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            device_id = instance.device_id
            self.perform_destroy(instance)
            return Response({
                "details": {
                    "message": f"Meter with device ID '{device_id}' was successfully deleted"
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error deleting meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({
                "details": {
                    "message": "Meter updated successfully",
                    "data": serializer.data
                }
            })
        except Exception as e:
            return Response({
                "error": "Error updating meter",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_update(self, serializer):
        """Custom perform_update method"""
        serializer.save()


class MeterAssignmentViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            assignments = MeterAssignment.objects.all()
            serializer = MeterAssignmentSerializer(assignments, many=True)
            return Response({
                "details": {
                    "message": "Meter assignments retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error retrieving meter assignments",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def destroy(self, request, pk):
        try:
            assignment_id = pk
            if not assignment_id:
                return Response({
                    "error": "Assignment ID is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            assignment = MeterAssignment.objects.get(id=assignment_id)
            assignment.delete()
            return Response(
                {
                    "details": {
                        "message": "Meter assignment deleted successfully"
                    }
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error deleting meter assignment",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
