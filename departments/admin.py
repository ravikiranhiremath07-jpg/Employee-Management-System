from django.contrib import admin
from departments.models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_code', 'name', 'employee_count', 'created_at')
    search_fields = ('department_code', 'name')
