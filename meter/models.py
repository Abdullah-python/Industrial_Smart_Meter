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
    engineer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_meters')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_made')
    status = models.CharField(max_length=10, choices=ASSIGNMENT_STATUS, default='ADMIN')
    assigned_at = models.DateTimeField(auto_now_add=True)
    previous_assignment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        # Validate assignment flow

        if self.engineer.role != 'ENGINEER':
            if self.status != 'ENGINEER':
                raise ValidationError("Manager can only assign to Engineer")
        elif self.manager.role == 'ENGINEER':
            raise ValidationError("Engineer cannot make assignments")

        # Validate assigned_to role matches status
        if self.status == 'MANAGER' and not self.engineer.is_manager():
            raise ValidationError("Assigned user must be a Manager")
        elif self.status == 'ENGINEER' and not self.manager.is_engineer():
            raise ValidationError("Assigned user must be an Engineer")

    def __str__(self):
        return f"{self.meter.device_id} - {self.engineer.username} to {self.manager.username} ({self.status})"

    class Meta:
        ordering = ['-assigned_at']
