from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User


# Create your models here.

class Meter(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_id} - {self.location}"

    class Meta:
        ordering = ['-created_at']


class MeterAssignment(models.Model):
    ASSIGNMENT_STATUS = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('ENGINEER', 'Engineer'),
    ]

    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)
    engineer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_meters', null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_made')
    status = models.CharField(max_length=10, choices=ASSIGNMENT_STATUS, default='ADMIN')
    assigned_at = models.DateTimeField(auto_now_add=True)
    previous_assignment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        errors = {}

        # Validate manager role
        if self.manager and self.manager.role != 'MANAGER':
            errors['manager'] = "Manager must be a user with MANAGER role"

        # Validate engineer role if engineer is assigned
        if self.engineer and self.engineer.role != 'ENGINEER':
            errors['engineer'] = "Engineer must be a user with ENGINEER role"

        # Validate assignment flow
        if self.status == 'ENGINEER' and not self.engineer:
            errors.setdefault('engineer', []).append("Engineer must be assigned for ENGINEER status")
        elif self.status == 'MANAGER' and not self.engineer:
            errors.setdefault('engineer', []).append("Engineer must be assigned for MANAGER status")

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.meter.device_id} - {self.engineer.username if self.engineer else 'None'} to {self.manager.username} ({self.status})"

    class Meta:
        ordering = ['-assigned_at']
