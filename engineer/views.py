from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from meter.models import MeterAssignment
from meter.serializers import MeterAssignmentSerializer, MeterSerializer
from meter.models import Meter
from accounts.models import User
# Create your views here.

class EngineersMeterViewSet(viewsets.ViewSet):
    """ViewSet for managing engineer operations"""

    def list(self, request):
        """List all meters assigned to the engineer"""
        try:
            if not (request.user.role in ['ENGINEER'] or request.user.is_superuser):
                return Response({
                    "error": "Unauthorized",
                    "details": "Only ENGINEER can view assigned meters"
                }, status=status.HTTP_403_FORBIDDEN)

            engineer = User.objects.get(id=request.user.id)
            meter_assignments = MeterAssignment.objects.filter(engineer=engineer)
            if not meter_assignments:
                return Response({
                    "error": "Not found",
                    "details": "No meters assigned to the engineer"
                }, status=status.HTTP_404_NOT_FOUND)

            meter_ids = [assignment.meter.id for assignment in meter_assignments]
            meters = Meter.objects.filter(id__in=meter_ids)

            if not meters:
                return Response({
                    "error": "Not found",
                    "details": "No meters assigned to the engineer"
                }, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "details": {
                    "message": "Meters retrieved successfully",
                    "data": {
                        'meter_assignments': MeterAssignmentSerializer(meter_assignments, many=True).data,
                        'meters': MeterSerializer(meters, many=True).data
                    }
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "Error fetching meters",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

