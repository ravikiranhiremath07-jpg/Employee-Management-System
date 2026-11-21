from django.db import models
from django.contrib.auth.models import User
from departments.models import Department

class Employee(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ON_LEAVE', 'On Leave'),
        ('TERMINATED', 'Terminated'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    emp_id = models.CharField(max_length=20, unique=True, verbose_name="Employee ID")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(verbose_name="Date of Birth")
    address = models.TextField()
    profile_photo = models.FileField(upload_to='employee_photos/', blank=True, null=True, verbose_name="Profile Photo")
    joining_date = models.DateField(verbose_name="Joining Date")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    designation = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name="Emergency Contact")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['emp_id']

    def __str__(self):
        return f"{self.emp_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def photo_url(self):
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            return self.profile_photo.url
        return None
