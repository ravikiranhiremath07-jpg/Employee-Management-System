from django.db import models

class Department(models.Model):
    department_code = models.CharField(max_length=20, unique=True, verbose_name="Department Code")
    name = models.CharField(max_length=100, unique=True, verbose_name="Department Name")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.department_code})"

    @property
    def employee_count(self):
        return self.employees.count()
