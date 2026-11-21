from django.contrib import admin
from employees.models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'first_name', 'last_name', 'department', 'designation', 'employment_status', 'joining_date')
    list_filter = ('department', 'employment_status', 'gender')
    search_fields = ('emp_id', 'first_name', 'last_name', 'email', 'phone')
