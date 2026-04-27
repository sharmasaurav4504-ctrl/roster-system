from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    ROLE_CHOICES = [
        ('WFM', 'Workforce Management'),
        ('Supervisor', 'Supervisor'),
        ('Agent', 'Agent'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    emp_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)
    pms = models.CharField(max_length=100, blank=True, null=True)
    manager = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.emp_id} - {self.name}"

class Roster(models.Model):
    SHIFT_CODES = [
        ('E', 'E'), ('E-2', 'E-2'), ('M', 'M'), ('A', 'A'), ('N', 'N'),
        ('CL', 'CL'), ('EL', 'EL'), ('UL', 'UL'), ('H', 'H'), ('ML', 'ML'), ('HY', 'HY'), ('WO', 'WO')
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='rosters')
    date = models.DateField()
    shift_code = models.CharField(max_length=10, choices=SHIFT_CODES)
    
    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['date']

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    LEAVE_CHOICES = [
        ('CL', 'Casual Leave'),
        ('UL', 'Unplanned Leave'),
        ('EL', 'Earned Leave'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=5, choices=LEAVE_CHOICES, default='CL')
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

class SwapRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    from_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='swaps_sent')
    to_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='swaps_received')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
