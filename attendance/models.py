from django.db import models
from employees.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('HALF_DAY', 'Half Day'),
        ('ON_LEAVE', 'On Leave'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(verbose_name="Attendance Date")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    check_in_time = models.TimeField(null=True, blank=True, verbose_name="Check In Time")
    check_out_time = models.TimeField(null=True, blank=True, verbose_name="Check Out Time")
    notes = models.TextField(blank=True, verbose_name="Notes / Remarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', 'employee__emp_id']

    def __str__(self):
        return f"{self.employee.emp_id} | {self.date} | {self.get_status_display()}"
