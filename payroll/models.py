from django.db import models
from employees.models import Employee

class Salary(models.Model):
    MONTH_CHOICES = (
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    )
    STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Basic Salary (₹/$)")
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Allowances")
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Deductions")
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, verbose_name="Net Salary")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Payment Date")
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, verbose_name="Notes / Remarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employee', 'month', 'year')
        ordering = ['-year', '-month']

    def save(self, *args, **kwargs):
        # Calculate Net Salary automatically: Net Salary = Basic Salary + Allowances - Deductions
        self.net_salary = (self.basic_salary or 0) + (self.allowances or 0) - (self.deductions or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.emp_id} | {self.get_month_display()} {self.year} | Net: {self.net_salary}"
