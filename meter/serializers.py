from rest_framework import serializers
from .models import Meter, MeterAssignment, MeterData
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

class MeterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeterData
        fields = [
            'id', 'meter', 'timestamp', 'engine_hours', 'frequency_hz', 'power_percentage',
            'avg_ll_volt', 'avg_ln_volt', 'avg_current',
            'phase_a_voltage_v', 'phase_a_current_a', 'phase_a_voltage_ll', 'phase_a_frequency_hz',
            'phase_a_real_power', 'phase_a_apparent_power', 'phase_a_reactive_power',
            'phase_b_voltage_v', 'phase_b_current_a', 'phase_b_voltage_ll', 'phase_b_frequency_hz',
            'phase_b_real_power', 'phase_b_apparent_power', 'phase_b_reactive_power',
            'phase_c_voltage_v', 'phase_c_current_a', 'phase_c_voltage_ll', 'phase_c_frequency_hz',
            'phase_c_real_power', 'phase_c_apparent_power', 'phase_c_reactive_power',
            'gen_breaker', 'util_breaker', 'gc_status',
            'coolant_temp_c', 'oil_pressure_kpa', 'battery_voltage_v', 'fuel_level_percent',
            'rpm', 'oil_temp_c', 'boost_pressure_kpa', 'intake_air_temp_c', 'fuel_rate_lph',
            'instantaneous_power_kw', 'alarm_emergency_stop', 'alarm_low_oil_pressure',
            'alarm_high_coolant_temp', 'alarm_low_coolant_level', 'alarm_crank_failure'
        ]
        read_only_fields = ['timestamp']


