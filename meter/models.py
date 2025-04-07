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

