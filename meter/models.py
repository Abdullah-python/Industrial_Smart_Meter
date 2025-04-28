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

    # Average readings
    avg_ll_volt = models.FloatField(null=True, blank=True, help_text="Average line-to-line voltage")
    avg_ln_volt = models.FloatField(null=True, blank=True, help_text="Average line-to-neutral voltage")
    avg_current = models.FloatField(null=True, blank=True, help_text="Average current")

    # Phase A data
    phase_a_voltage_v = models.FloatField()
    phase_a_current_a = models.FloatField()
    phase_a_voltage_ll = models.FloatField(null=True, blank=True, help_text="Phase A line-to-line voltage")
    phase_a_frequency_hz = models.FloatField(null=True, blank=True, help_text="Phase A frequency")
    phase_a_real_power = models.FloatField(null=True, blank=True, help_text="Phase A real power")
    phase_a_apparent_power = models.FloatField(null=True, blank=True, help_text="Phase A apparent power")
    phase_a_reactive_power = models.FloatField(null=True, blank=True, help_text="Phase A reactive power")

    # Phase B data
    phase_b_voltage_v = models.FloatField()
    phase_b_current_a = models.FloatField()
    phase_b_voltage_ll = models.FloatField(null=True, blank=True, help_text="Phase B line-to-line voltage")
    phase_b_frequency_hz = models.FloatField(null=True, blank=True, help_text="Phase B frequency")
    phase_b_real_power = models.FloatField(null=True, blank=True, help_text="Phase B real power")
    phase_b_apparent_power = models.FloatField(null=True, blank=True, help_text="Phase B apparent power")
    phase_b_reactive_power = models.FloatField(null=True, blank=True, help_text="Phase B reactive power")

    # Phase C data
    phase_c_voltage_v = models.FloatField()
    phase_c_current_a = models.FloatField()
    phase_c_voltage_ll = models.FloatField(null=True, blank=True, help_text="Phase C line-to-line voltage")
    phase_c_frequency_hz = models.FloatField(null=True, blank=True, help_text="Phase C frequency")
    phase_c_real_power = models.FloatField(null=True, blank=True, help_text="Phase C real power")
    phase_c_apparent_power = models.FloatField(null=True, blank=True, help_text="Phase C apparent power")
    phase_c_reactive_power = models.FloatField(null=True, blank=True, help_text="Phase C reactive power")

    # Breaker statuses
    gen_breaker = models.CharField(max_length=20, null=True, blank=True, help_text="Generator breaker status")
    util_breaker = models.CharField(max_length=20, null=True, blank=True, help_text="Utility breaker status")
    gc_status = models.CharField(max_length=20, null=True, blank=True, help_text="GC status")

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

