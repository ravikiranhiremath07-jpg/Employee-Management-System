from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Count, Q

from attendance.models import Attendance
from attendance.forms import AttendanceMarkForm
from employees.models import Employee
from departments.models import Department
from accounts.decorators import hr_or_admin_required, log_action

@login_required
@hr_or_admin_required
def attendance_list_view(request):
    date_filter = request.GET.get('date', '').strip()
    month_filter = request.GET.get('month', '').strip()
    status_filter = request.GET.get('status', '').strip()
    dept_filter = request.GET.get('department', '').strip()
    search_query = request.GET.get('search', '').strip()

    attendances = Attendance.objects.select_related('employee', 'employee__department').order_by('-date', 'employee__emp_id')

    if date_filter:
        attendances = attendances.filter(date=date_filter)

    if month_filter:
        try:
            year, month = [int(x) for x in month_filter.split('-')]
            attendances = attendances.filter(date__year=year, date__month=month)
        except Exception:
            pass

    if status_filter:
        attendances = attendances.filter(status=status_filter)

    if dept_filter:
        attendances = attendances.filter(employee__department_id=dept_filter)

    if search_query:
        attendances = attendances.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__emp_id__icontains=search_query)
        )

    # Monthly Summary statistics
    total_count = attendances.count()
    present_count = attendances.filter(status='PRESENT').count()
    absent_count = attendances.filter(status='ABSENT').count()
    half_day_count = attendances.filter(status='HALF_DAY').count()
    leave_count = attendances.filter(status='ON_LEAVE').count()

    attendance_percentage = round(((present_count + 0.5 * half_day_count) / total_count * 100), 1) if total_count > 0 else 0

    paginator = Paginator(attendances, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    return render(request, 'attendance_list.html', {
        'page_obj': page_obj,
        'departments': departments,
        'date_filter': date_filter,
        'month_filter': month_filter,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'search_query': search_query,
        'total_count': total_count,
        'present_count': present_count,
        'absent_count': absent_count,
        'half_day_count': half_day_count,
        'leave_count': leave_count,
        'attendance_percentage': attendance_percentage,
    })

@login_required
@hr_or_admin_required
def attendance_mark_view(request):
    if request.method == 'POST':
        form = AttendanceMarkForm(request.POST)
        if form.is_valid():
            att = form.save()
            log_action(request, "Marked Attendance", f"Marked {att.get_status_display()} for {att.employee.emp_id} on {att.date}")
            messages.success(request, f"Attendance for {att.employee.full_name} on {att.date} saved successfully!")
            return redirect('attendance_list')
    else:
        form = AttendanceMarkForm()

    return render(request, 'attendance_mark.html', {'form': form, 'title': 'Mark Daily Attendance'})

@login_required
@hr_or_admin_required
def attendance_edit_view(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceMarkForm(request.POST, instance=attendance)
        if form.is_valid():
            att = form.save()
            log_action(request, "Updated Attendance", f"Updated attendance for {att.employee.emp_id} on {att.date}")
            messages.success(request, f"Attendance record updated successfully.")
            return redirect('attendance_list')
    else:
        form = AttendanceMarkForm(instance=attendance)

    return render(request, 'attendance_mark.html', {'form': form, 'title': 'Edit Attendance Record', 'attendance': attendance})

@login_required
def my_attendance_view(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "No employee record associated with your account.")
        return redirect('dashboard')

    attendances = Attendance.objects.filter(employee=employee).order_by('-date')
    total_records = attendances.count()
    present_days = attendances.filter(status='PRESENT').count()
    absent_days = attendances.filter(status='ABSENT').count()
    half_days = attendances.filter(status='HALF_DAY').count()
    leave_days = attendances.filter(status='ON_LEAVE').count()

    att_pct = round(((present_days + 0.5 * half_days) / total_records * 100), 1) if total_records > 0 else 0

    paginator = Paginator(attendances, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'attendance_my.html', {
        'page_obj': page_obj,
        'employee': employee,
        'total_records': total_records,
        'present_days': present_days,
        'absent_days': absent_days,
        'half_days': half_days,
        'leave_days': leave_days,
        'att_pct': att_pct,
    })
