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

        # Get meters assigned to engineers and group them by engineer
        engineer_meters = MeterAssignment.objects.filter(engineer__in=engineer_ids)
        meter_serializer = MeterSerializer(
            Meter.objects.filter(id__in=engineer_meters.values_list('meter_id', flat=True)),
            many=True
        )

        # Create a dictionary to store meters for each engineer
        engineer_meter_map = {}
        for assignment in engineer_meters:
            engineer_id = assignment.engineer_id
            if engineer_id not in engineer_meter_map:
                engineer_meter_map[engineer_id] = []
            meter = Meter.objects.get(id=assignment.meter_id)
            engineer_meter_map[engineer_id].append(MeterSerializer(meter).data)

        # Add meters to each engineer's data
        response_data = []
        for engineer in engineer_serializer.data:
            engineer_id = engineer['id']
            engineer['meters'] = engineer_meter_map.get(engineer_id, [])
            response_data.append(engineer)

        return Response(response_data)


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

        return Response({
            'message': 'Meter assigned to engineer successfully',
            'meter_assignment': MeterAssignmentSerializer(meter_assignment).data,
            'meter': MeterSerializer(meter).data,
            'engineer': UserSerializer(engineer).data
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        """Delete a meter from an engineer"""
        if not (request.user.role in ['MANAGER'] or request.user.is_superuser):
            return Response({
                'message': 'Only MANAGER can delete meters from engineers'
            }, status=status.HTTP_403_FORBIDDEN)

        meter_id = request.data.get('meter_id')
        engineer_id = request.data.get('engineer_id')

        meter_assignment = MeterAssignment.objects.filter(meter_id=meter_id, manager=request.user).first()
        if not meter_assignment:
            return Response({
                'message': 'Meter is not assigned to the user'
            }, status=status.HTTP_400_BAD_REQUEST)

        engineer_assignment = UserAssignment.objects.filter(engineer_id=engineer_id, manager=request.user).first()
        if not engineer_assignment:
            return Response({
                'message': 'Engineer is not assigned to the user'
            }, status=status.HTTP_400_BAD_REQUEST)

        meter_assignment.engineer = None
        meter_assignment.save()

        return Response({
            'message': 'Meter unassigned from engineer successfully',
            'meter_assignment': MeterAssignmentSerializer(meter_assignment).data,
            'meter': MeterSerializer(meter_assignment.meter).data,
            'engineer': UserSerializer(meter_assignment.engineer).data
        }, status=status.HTTP_200_OK)






