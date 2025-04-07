from django.db import models
from accounts.models import User

# Create your models here.

class UserAssignment(models.Model):
    """
    Relationship model to assign engineers to managers
    """
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_engineers')
    engineer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managers')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('manager', 'engineer')
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.engineer.username} assigned to {self.manager.username}"


