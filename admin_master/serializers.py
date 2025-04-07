from rest_framework import serializers
from .models import UserAssignment

class UserAssignmentSerializer(serializers.ModelSerializer):
    manager_username = serializers.CharField(source='manager.username', read_only=True)
    engineer_username = serializers.CharField(source='engineer.username', read_only=True)

    class Meta:
        model = UserAssignment
        fields = ('id', 'manager', 'engineer', 'manager_username', 'engineer_username', 'assigned_at')
        read_only_fields = ('id', 'assigned_at', 'manager_username', 'engineer_username')
