from rest_framework import serializers
from .models import Meter, MeterAssignment
from django.core.exceptions import ValidationError

class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = ['id', 'device_id', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class MeterAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterAssignment
        fields = ['id', 'meter', 'engineer', 'manager', 'status', 'assigned_at', 'previous_assignment']
        read_only_fields = ['assigned_at']

    def validate(self, data):
        # Create a temporary instance for validation
        instance = MeterAssignment(**data)

        # Call the model's clean method to validate
        try:
            instance.clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else e.messages)

        return data

    def create(self, validated_data):
        instance = MeterAssignment(**validated_data)
        instance.clean()  # Call clean before saving
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.clean()  # Call clean before saving
        instance.save()
        return instance


