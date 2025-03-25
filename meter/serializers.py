from rest_framework import serializers
from .models import Meter

class MeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meter
        fields = ['id', 'device_id', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']