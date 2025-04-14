from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from accounts.models import User
from accounts.serializers import UserSerializer
from admin_master.models import UserAssignment
from admin_master.serializers import UserAssignmentSerializer
from rest_framework import status
from meter.models import Meter, MeterAssignment
from meter.serializers import MeterSerializer, MeterAssignmentSerializer

# Create your views here.

class AssignedEngineerViewSet(viewsets.ViewSet):
    """ViewSet for managing manager operations"""

    def list(self, request):
        """List all engineers assigned to the manager"""
        if not (request.user.role in ['MANAGER'] or request.user.is_superuser):
            return Response({
                'message': 'Only MANAGER can view assigned engineers'
            }, status=status.HTTP_403_FORBIDDEN)
        engineers = UserAssignment.objects.filter(manager=request.user)
        engineer_manager_assignments = UserAssignmentSerializer(engineers, many=True)

        engineer_ids = [assignment['engineer'] for assignment in engineer_manager_assignments.data]
        engineers = User.objects.filter(id__in=engineer_ids)
        engineer_serializer = UserSerializer(engineers, many=True)

        return Response({
            'engineer_manager_assignments': engineer_manager_assignments.data,
            'engineers': engineer_serializer.data
        })


class AssignedMetersViewSet(viewsets.ViewSet):
    """ViewSet for managing manager operations"""

    def list(self, request):
        """List all meters assigned to the manager"""
        if not (request.user.role in ['MANAGER'] or request.user.is_superuser):
            return Response({
                'message': 'Only MANAGER can view assigned meters'
            }, status=status.HTTP_403_FORBIDDEN)

        # Get all meter assignments for the manager
        meter_assignments = MeterAssignment.objects.filter(manager=request.user)

        # Get all meter IDs from the assignments
        meter_ids = [assignment.meter.id for assignment in meter_assignments]

        # Get all meters with those IDs
        meters = Meter.objects.filter(id__in=meter_ids)

        # Serialize both the assignments and meters
        assignment_serializer = MeterAssignmentSerializer(meter_assignments, many=True)
        meter_serializer = MeterSerializer(meters, many=True)

        return Response({
            'assignments': assignment_serializer.data,
            'meters': meter_serializer.data
        })


class AssignMeterToEngineerViewSet(viewsets.ViewSet):
    """ViewSet for managing manager operations"""

    def create(self, request):
        """Assign a meter to an engineer"""
        if not (request.user.role in ['MANAGER'] or request.user.is_superuser):
            return Response({
                'message': 'Only MANAGER can assign meters to engineers'
            }, status=status.HTTP_403_FORBIDDEN)

        meter = Meter.objects.get(id=request.data.get('meter_id'))
        engineer = User.objects.get(id=request.data.get('engineer_id'))
        if not meter or not engineer:
            return Response({
                'message': 'Meter or engineer not found'
            }, status=status.HTTP_404_NOT_FOUND)

        engineer_manager_assignment = UserAssignment.objects.filter(engineer=engineer, manager=request.user).first()
        if not engineer_manager_assignment:
            return Response({
                'message': 'Engineer is not assigned to the user'
            }, status=status.HTTP_400_BAD_REQUEST)

        meter_assignment = MeterAssignment.objects.filter(meter=meter, manager=request.user).first()
        if not meter_assignment:
            return Response({
                'message': 'Meter is not assigned to the user'
            }, status=status.HTTP_400_BAD_REQUEST)
        meter_assignment.engineer = engineer
        meter_assignment.save()

        return Response(MeterAssignmentSerializer(meter_assignment).data)





