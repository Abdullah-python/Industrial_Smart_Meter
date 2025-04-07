from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from accounts.models import User
from admin_master.models import UserAssignment
from accounts.serializers import UserSerializer
from rest_framework import status
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
        serializer = UserSerializer(engineers, many=True)
        return Response(serializer.data)



