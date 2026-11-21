from django.contrib import admin
from attendance.models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'date')
    search_fields = ('employee__emp_id', 'employee__first_name', 'employee__last_name')
