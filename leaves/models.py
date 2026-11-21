from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    year = models.PositiveIntegerField()
    casual_leave = models.PositiveIntegerField(default=12, verbose_name="Casual Leave")
    sick_leave = models.PositiveIntegerField(default=10, verbose_name="Sick Leave")
    earned_leave = models.PositiveIntegerField(default=15, verbose_name="Earned Leave")

    class Meta:
        unique_together = ('employee', 'year')

    def __str__(self):
        return f"{self.employee.emp_id} - Year {self.year} Balances"

    @property
    def total_leave_balance(self):
        return self.casual_leave + self.sick_leave + self.earned_leave


class LeaveApplication(models.Model):
    LEAVE_TYPE_CHOICES = (
        ('CASUAL', 'Casual Leave'),
        ('SICK', 'Sick Leave'),
        ('EARNED', 'Earned Leave'),
        ('OTHER', 'Other / Special Leave'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, default='CASUAL')
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    total_days = models.PositiveIntegerField(default=1, verbose_name="Total Days")
    reason = models.TextField(verbose_name="Reason for Leave")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    review_comment = models.TextField(blank=True, verbose_name="Review Remarks")
    reviewed_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.employee.emp_id} | {self.get_leave_type_display()} ({self.start_date} to {self.end_date}) - {self.status}"
