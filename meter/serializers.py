from rest_framework import serializers
from .models import Meter, MeterAssignment

class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = ['id', 'device_id', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class MeterAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterAssignment
        fields = ['id', 'meter', 'assigned_to', 'assigned_by', 'status', 'assigned_at', 'previous_assignment']
        read_only_fields = ['assigned_at']

