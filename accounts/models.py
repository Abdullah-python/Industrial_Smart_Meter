from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """
    Custom user model with role-based permissions
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MANAGER', 'Manager'),
        ('ENGINEER', 'Engineer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ENGINEER')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128, blank=True)


    class Meta:
        ordering = ['username']

    def is_admin(self):
        return self.role == 'ADMIN'

    def is_manager(self):
        return self.role == 'MANAGER'

    def is_engineer(self):
        return self.role == 'ENGINEER'

