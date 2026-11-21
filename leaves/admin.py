from django.contrib import admin
from leaves.models import LeaveApplication, LeaveBalance

@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'applied_on')
    list_filter = ('status', 'leave_type', 'applied_on')
    search_fields = ('employee__emp_id', 'employee__first_name', 'employee__last_name')

@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'year', 'casual_leave', 'sick_leave', 'earned_leave')
    search_fields = ('employee__emp_id', 'employee__first_name')
