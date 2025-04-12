from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import UserAssignment
from accounts.models import User
from .serializers import UserAssignmentSerializer
from accounts.serializers import UserSerializer

# Create your views here.


class UsersViewSet(viewsets.ViewSet):
    """ViewSet for listing all users"""
    def list(self, request):
        if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
            return Response({
                'message': 'Only ADMIN can assign engineers'
            }, status=status.HTTP_403_FORBIDDEN)

        """List all users"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserAssignmentViewSet(viewsets.ViewSet):
    """ViewSet for assigning engineers to managers"""

    def create(self, request):
        """Assign an engineer to a manager"""
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        print(request.user, 'useree')

        # Check if the user is admin, manager, or a Django superuser
        if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
            return Response({
                'message': 'Only ADMIN can assign engineers'
            }, status=status.HTTP_403_FORBIDDEN)

        manager_id = request.data.get('manager_id')
        engineer_id = request.data.get('engineer_id')

        # If user is a manager, they can only assign engineers to themselves
        if request.user.role == 'MANAGER' and str(request.user.id) != str(manager_id):
            return Response({
                'message': 'Managers can only assign engineers to themselves'
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            manager = User.objects.get(id=manager_id, role='MANAGER')
            engineer = User.objects.get(id=engineer_id, role='ENGINEER')
        except User.DoesNotExist:
            return Response({
                'message': 'Manager or engineer not found or invalid role'
            }, status=status.HTTP_404_NOT_FOUND)

        # Create assignment
        assignment, created = UserAssignment.objects.get_or_create(
            manager=manager,
            engineer=engineer
        )

        if created:
            return Response({
                'message': f'Engineer {engineer.username} assigned to manager {manager.username}',
                'assignment': UserAssignmentSerializer(assignment).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': f'Engineer {engineer.username} is already assigned to manager {manager.username}',
                'assignment': UserAssignmentSerializer(assignment).data
            }, status=status.HTTP_200_OK)

    def list(self, request):
        """List all assignments"""
        if not (request.user.role in ['ADMIN'] or request.user.is_superuser):
            return Response({
                'message': 'Only ADMIN can assign engineers'
            }, status=status.HTTP_403_FORBIDDEN)
        assignments = UserAssignment.objects.all()
        serializer = UserAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Delete an assignment"""
        assignment = UserAssignment.objects.get(id=pk)
        assignment.delete()
        return Response({
            'message': 'Assignment deleted successfully'
        }, status=status.HTTP_200_OK)

