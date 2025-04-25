from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User


# Create your models here.

class Meter(models.Model):
    id = models.AutoField(primary_key=True)
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

        # Check if meter is already assigned to this manager
        if not self.pk and MeterAssignment.objects.filter(meter=self.meter, manager=self.manager, status=self.status).exists():
            errors['manager'] = "This meter is already assigned to this manager with the same status"

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



class MeterData(models.Model):
    id = models.AutoField(primary_key=True)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField(auto_now_add=True)

    # Basic meter data
    engine_hours = models.FloatField()
    frequency_hz = models.FloatField(help_text="Frequency of the generator in hertz")
    power_percentage = models.IntegerField()

    # Phase A data
    phase_a_voltage_v = models.FloatField()
    phase_a_current_a = models.FloatField()

    # Phase B data
    phase_b_voltage_v = models.FloatField()
    phase_b_current_a = models.FloatField()

    # Phase C data
    phase_c_voltage_v = models.FloatField()
    phase_c_current_a = models.FloatField()

    # Temperature and pressure readings
    coolant_temp_c = models.IntegerField(help_text="Coolant temperature in Celsius")
    oil_pressure_kpa = models.IntegerField(help_text="Oil pressure in kilopascals")
    battery_voltage_v = models.FloatField(help_text="Battery voltage in volts")
    fuel_level_percent = models.IntegerField(help_text="Fuel level in percentage")
    rpm = models.IntegerField(help_text="Engine RPM")
    oil_temp_c = models.IntegerField(help_text="Oil temperature in Celsius")
    boost_pressure_kpa = models.IntegerField(help_text="Boost pressure in kilopascals")
    intake_air_temp_c = models.IntegerField(help_text="Intake air temperature in Celsius")
    fuel_rate_lph = models.FloatField(help_text="Fuel rate in liters per hour")
    instantaneous_power_kw = models.FloatField(help_text="Instantaneous power in kilowatts")

    # Alarm states
    alarm_emergency_stop = models.BooleanField(default=False)
    alarm_low_oil_pressure = models.BooleanField(default=False)
    alarm_high_coolant_temp = models.BooleanField(default=False)
    alarm_low_coolant_level = models.BooleanField(default=False)
    alarm_crank_failure = models.BooleanField(default=False)



    def __str__(self):
        return f"Data for {self.meter.device_id} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Meter Data"
        verbose_name_plural = "Meter Data"

