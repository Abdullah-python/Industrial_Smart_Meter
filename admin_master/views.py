from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import UserAssignment
from accounts.models import User
from .serializers import UserAssignmentSerializer
from meter.models import MeterAssignment, Meter
from meter.serializers import MeterAssignmentSerializer, MeterSerializer
from accounts.serializers import UserSerializer

# Create your views here.


class UsersViewSet(viewsets.ViewSet):
    """ViewSet for listing all users"""
    def list(self, request):
        try:
            if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
                return Response({
                    "details": {
                        "message": "Only ADMIN can assign engineers",
                        "data": None
                    }
                }, status=status.HTTP_403_FORBIDDEN)

            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response({
                "details": {
                    "message": "Users retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error retrieving users",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserAssignmentViewSet(viewsets.ViewSet):
    """ViewSet for assigning engineers to managers"""

    def create(self, request):
        """Assign an engineer to a manager"""
        try:
            if not request.user.is_authenticated:
                return Response({
                    "details": {
                        "message": "Authentication required",
                        "data": None
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
                return Response({
                    "details": {
                        "message": "Only ADMIN can assign engineers",
                        "data": None
                    }
                }, status=status.HTTP_403_FORBIDDEN)

            manager_id = request.data.get('manager_id')
            engineer_id = request.data.get('engineer_id')

            if request.user.role == 'MANAGER' and str(request.user.id) != str(manager_id):
                return Response({
                    "details": {
                        "message": "Managers can only assign engineers to themselves",
                        "data": None
                    }
                }, status=status.HTTP_403_FORBIDDEN)

            try:
                manager = User.objects.get(id=manager_id, role='MANAGER')
                engineer = User.objects.get(id=engineer_id, role='ENGINEER')
            except User.DoesNotExist:
                return Response({
                    "details": {
                        "message": "Manager or engineer not found or invalid role",
                        "data": None
                    }
                }, status=status.HTTP_404_NOT_FOUND)

            assignment, created = UserAssignment.objects.get_or_create(
                manager=manager,
                engineer=engineer
            )

            if created:
                return Response({
                    "details": {
                        "message": f'Engineer {engineer.username} assigned to manager {manager.username}',
                        "data": UserAssignmentSerializer(assignment).data
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "details": {
                        "message": f'Engineer {engineer.username} is already assigned to manager {manager.username}',
                        "data": UserAssignmentSerializer(assignment).data
                    }
                }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error creating assignment",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """List all engineer and manager assignments"""
        try:
            if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
                return Response({
                    "details": {
                        "message": "Only ADMIN can assign engineers",
                        "data": None
                    }
                }, status=status.HTTP_403_FORBIDDEN)

            assignments = UserAssignment.objects.all()
            serializer = UserAssignmentSerializer(assignments, many=True)
            return Response({
                "details": {
                    "message": "Assignments retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error retrieving assignments",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Delete an engineer from a manager"""
        try:
            if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
                return Response({
                    "details": {
                        "message": "Only ADMIN can delete assignments",
                        "data": None
                    }
                }, status=status.HTTP_403_FORBIDDEN)

            assignment = UserAssignment.objects.get(id=pk)
            if not assignment:
                return Response({
                    "details": {
                        "message": "Assignment not found",
                        "data": None
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            meter_assignments = MeterAssignment.objects.filter(manager=assignment.manager)
            if meter_assignments:
                for meter_assignment in meter_assignments:
                    meter_assignment.engineer = None
                    meter_assignment.save()

            assignment.delete()
            return Response({
                "details": {
                    "message": "Assignment deleted successfully",
                    "data": None
                }
            }, status=status.HTTP_200_OK)
        except UserAssignment.DoesNotExist:
            return Response({
                "details": {
                    "message": "Assignment not found",
                    "data": None
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error deleting assignment",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ManagerViewSet(viewsets.ViewSet):
    """ViewSet for listing all managers"""
    def list(self, request):
        try:
            managers = User.objects.filter(role='MANAGER')
            serializer = UserSerializer(managers, many=True)
            return Response({
                "details": {
                    "message": "Managers retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error retrieving managers",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        try:
            manager = User.objects.get(id=pk, role='MANAGER')
            assignments = MeterAssignment.objects.filter(manager=manager)
            assignments_serializer = MeterAssignmentSerializer(assignments, many=True)
            engineer_assignments = UserAssignment.objects.filter(manager=manager)
            engineer_assignments_serializer = UserAssignmentSerializer(engineer_assignments, many=True)

            meters = Meter.objects.filter(id__in=assignments.values_list('meter', flat=True))
            meters_serializer = MeterSerializer(meters, many=True)
            engineers = User.objects.filter(id__in=engineer_assignments.values_list('engineer', flat=True))
            engineers_serializer = UserSerializer(engineers, many=True)

            serializer = UserSerializer(manager)
            return Response({
                "details": {
                    "message": "Manager retrieved successfully",
                    "data": {
                        "manager": serializer.data,
                        "meter_assignments": assignments_serializer.data,
                        "engineer_assignments": engineer_assignments_serializer.data,
                        "meters": meters_serializer.data,
                        "engineers": engineers_serializer.data
                    }
                }
            })
        except User.DoesNotExist:
            return Response({
                "details": {
                    "message": "Manager not found",
                    "data": None
                }
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error retrieving manager",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EngineerViewSet(viewsets.ViewSet):
    """ViewSet for listing all engineers"""
    def list(self, request):
        try:
            engineers = User.objects.filter(role='ENGINEER')
            serializer = UserSerializer(engineers, many=True)
            return Response({
                "details": {
                    "message": "Engineers retrieved successfully",
                    "data": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "details": {
                    "message": "Error retrieving engineers",
                    "data": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
