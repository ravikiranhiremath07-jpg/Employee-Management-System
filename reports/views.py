import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import date

from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leaves.models import LeaveApplication
from payroll.models import Salary
from accounts.decorators import hr_or_admin_required, log_action

@login_required
@hr_or_admin_required
def reports_dashboard_view(request):
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    total_attendances = Attendance.objects.count()
    total_leaves = LeaveApplication.objects.count()
    total_salaries = Salary.objects.count()

    departments = Department.objects.all()
    current_year = date.today().year
    years = range(current_year - 4, current_year + 2)

    return render(request, 'reports.html', {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_attendances': total_attendances,
        'total_leaves': total_leaves,
        'total_salaries': total_salaries,
        'departments': departments,
        'years': years,
    })

@login_required
@hr_or_admin_required
def export_employees_csv(request):
    dept_id = request.GET.get('department')
    status = request.GET.get('status')

    qs = Employee.objects.select_related('department')
    if dept_id:
        qs = qs.filter(department_id=dept_id)
    if status:
        qs = qs.filter(employment_status=status)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="employees_report_{timezone.localdate()}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Gender',
        'Date of Birth', 'Department', 'Designation', 'Joining Date',
        'Employment Status', 'Emergency Contact', 'Address'
    ])

    for emp in qs:
        writer.writerow([
            emp.emp_id, emp.first_name, emp.last_name, emp.email, emp.phone,
            emp.gender, emp.date_of_birth,
            emp.department.name if emp.department else 'N/A',
            emp.designation, emp.joining_date, emp.employment_status,
            emp.emergency_contact, emp.address.replace('\n', ' ')
        ])

    log_action(request, "Exported Employee Report", f"Exported {qs.count()} employee records to CSV")
    return response

@login_required
@hr_or_admin_required
def export_attendance_csv(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    dept_id = request.GET.get('department')

    qs = Attendance.objects.select_related('employee', 'employee__department')
    if month:
        qs = qs.filter(date__month=month)
    if year:
        qs = qs.filter(date__year=year)
    if dept_id:
        qs = qs.filter(employee__department_id=dept_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{timezone.localdate()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Employee ID', 'Employee Name', 'Department', 'Status', 'Check In', 'Check Out', 'Notes'])

    for att in qs:
        writer.writerow([
            att.date, att.employee.emp_id, att.employee.full_name,
            att.employee.department.name if att.employee.department else 'N/A',
            att.get_status_display(), att.check_in_time or '', att.check_out_time or '',
            att.notes
        ])

    log_action(request, "Exported Attendance Report", f"Exported {qs.count()} attendance records to CSV")
    return response

@login_required
@hr_or_admin_required
def export_leaves_csv(request):
    status = request.GET.get('status')
    leave_type = request.GET.get('leave_type')

    qs = LeaveApplication.objects.select_related('employee', 'employee__department', 'reviewed_by')
    if status:
        qs = qs.filter(status=status)
    if leave_type:
        qs = qs.filter(leave_type=leave_type)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="leave_report_{timezone.localdate()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Applied On', 'Employee ID', 'Employee Name', 'Department', 'Leave Type', 'Start Date', 'End Date', 'Total Days', 'Status', 'Reason', 'Reviewed By', 'Review Comment'])

    for lv in qs:
        writer.writerow([
            lv.applied_on.strftime('%Y-%m-%d %H:%M'),
            lv.employee.emp_id, lv.employee.full_name,
            lv.employee.department.name if lv.employee.department else 'N/A',
            lv.get_leave_type_display(), lv.start_date, lv.end_date, lv.total_days,
            lv.get_status_display(), lv.reason.replace('\n', ' '),
            lv.reviewed_by.username if lv.reviewed_by else 'N/A',
            lv.review_comment
        ])

    log_action(request, "Exported Leave Report", f"Exported {qs.count()} leave records to CSV")
    return response

@login_required
@hr_or_admin_required
def export_salaries_csv(request):
    month = request.GET.get('month')
    year = request.GET.get('year')

    qs = Salary.objects.select_related('employee', 'employee__department')
    if month:
        qs = qs.filter(month=month)
    if year:
        qs = qs.filter(year=year)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="salary_report_{timezone.localdate()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Month', 'Year', 'Employee ID', 'Employee Name', 'Department', 'Basic Salary', 'Allowances', 'Deductions', 'Net Salary', 'Payment Status', 'Payment Date', 'Notes'])

    for sal in qs:
        writer.writerow([
            sal.get_month_display(), sal.year, sal.employee.emp_id, sal.employee.full_name,
            sal.employee.department.name if sal.employee.department else 'N/A',
            sal.basic_salary, sal.allowances, sal.deductions, sal.net_salary,
            sal.get_payment_status_display(), sal.payment_date or '', sal.notes
        ])

    log_action(request, "Exported Salary Report", f"Exported {qs.count()} salary records to CSV")
    return response

@login_required
@hr_or_admin_required
def export_departments_csv(request):
    departments = Department.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="departments_report_{timezone.localdate()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Department Code', 'Department Name', 'Description', 'Total Employees', 'Active Employees'])

    for d in departments:
        writer.writerow([
            d.department_code, d.name, d.description.replace('\n', ' '),
            d.employees.count(),
            d.employees.filter(employment_status='ACTIVE').count()
        ])

    log_action(request, "Exported Departments Report", f"Exported {departments.count()} department records to CSV")
    return response
