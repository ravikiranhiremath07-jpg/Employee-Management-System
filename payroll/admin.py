from django.contrib import admin
from payroll.models import Salary

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'payment_status', 'payment_date')
    list_filter = ('year', 'month', 'payment_status')
    search_fields = ('employee__emp_id', 'employee__first_name', 'employee__last_name')
