from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User
from meter.models import Meter
from meter.serializers import MeterSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'confirm_password',
                 'first_name', 'last_name', 'role')
        read_only_fields = ('id',)
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': False},
            'email': {'required': True},
            'role': {'required': True}
        }

    def validate(self, data):
        # Validate passwords match
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")

        # Validate role
        role = data.get('role')
        if role not in ['ADMIN', 'MANAGER', 'ENGINEER']:
            raise serializers.ValidationError("Role must be ADMIN, MANAGER or ENGINEER")

        return data

    def create(self, validated_data):
        # Remove confirm_password from the data
        validated_data.pop('confirm_password', None)

        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role']
        )
        return user


