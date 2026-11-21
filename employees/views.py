from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from employees.models import Employee
from departments.models import Department
from employees.forms import EmployeeAddForm, EmployeeEditForm, EmployeeSelfUpdateForm
from accounts.decorators import hr_or_admin_required, log_action
from attendance.models import Attendance
from leaves.models import LeaveApplication, LeaveBalance
from payroll.models import Salary

@login_required
@hr_or_admin_required
def employee_list_view(request):
    search_query = request.GET.get('search', '').strip()
    dept_id = request.GET.get('department', '').strip()
    status_filter = request.GET.get('status', '').strip()

    employees = Employee.objects.select_related('department', 'user').order_by('emp_id')

    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(emp_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(designation__icontains=search_query)
        )

    if dept_id:
        employees = employees.filter(department_id=dept_id)

    if status_filter:
        employees = employees.filter(employment_status=status_filter)

    paginator = Paginator(employees, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    return render(request, 'employee_list.html', {
        'page_obj': page_obj,
        'departments': departments,
        'search_query': search_query,
        'selected_dept': dept_id,
        'selected_status': status_filter,
    })

@login_required
@hr_or_admin_required
def employee_add_view(request):
    if request.method == 'POST':
        form = EmployeeAddForm(request.POST, request.FILES)
        if form.is_valid():
            emp = form.save()
            log_action(request, "Employee Added", f"Added employee {emp.full_name} ({emp.emp_id})")
            messages.success(request, f"Employee {emp.full_name} ({emp.emp_id}) created successfully!")
            return redirect('employee_detail', pk=emp.pk)
    else:
        form = EmployeeAddForm()

    return render(request, 'employee_add.html', {'form': form})

@login_required
@hr_or_admin_required
def employee_edit_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            emp = form.save()
            # Also update User model names and email
            user = emp.user
            user.first_name = emp.first_name
            user.last_name = emp.last_name
            user.email = emp.email
            user.save()

            log_action(request, "Employee Updated", f"Updated details for employee {emp.emp_id}")
            messages.success(request, f"Employee {emp.full_name} updated successfully!")
            return redirect('employee_detail', pk=emp.pk)
    else:
        form = EmployeeEditForm(instance=employee)

    return render(request, 'employee_edit.html', {'form': form, 'employee': employee})

@login_required
def employee_detail_view(request, pk):
    employee = get_object_or_404(Employee.objects.select_related('department', 'user'), pk=pk)

    # Permission check: Employees can only view their own detail profile
    user = request.user
    is_staff_or_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'HR'])
    if not is_staff_or_admin:
        if not hasattr(user, 'employee_profile') or user.employee_profile.pk != employee.pk:
            messages.error(request, "You are not authorized to view other employees' profiles.")
            return redirect('dashboard')

    # Related records for detail view
    recent_attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:10]
    recent_leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_on')[:5]
    leave_balances = LeaveBalance.objects.filter(employee=employee).order_by('-year').first()
    recent_salaries = Salary.objects.filter(employee=employee).order_by('-year', '-month')[:5]

    return render(request, 'employee_detail.html', {
        'employee': employee,
        'recent_attendances': recent_attendances,
        'recent_leaves': recent_leaves,
        'leave_balances': leave_balances,
        'recent_salaries': recent_salaries,
        'is_staff_or_admin': is_staff_or_admin,
    })

@login_required
@hr_or_admin_required
def employee_delete_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        action_type = request.POST.get('action_type', 'deactivate')
        if action_type == 'delete':
            emp_name = employee.full_name
            emp_id = employee.emp_id
            user = employee.user
            employee.delete()
            user.delete()
            log_action(request, "Employee Deleted", f"Permanently deleted employee {emp_name} ({emp_id})")
            messages.success(request, f"Employee {emp_name} ({emp_id}) was permanently deleted.")
        else:
            employee.employment_status = 'INACTIVE'
            employee.save()
            employee.user.is_active = False
            employee.user.save()
            log_action(request, "Employee Deactivated", f"Deactivated employee {employee.full_name} ({employee.emp_id})")
            messages.success(request, f"Employee {employee.full_name} deactivated successfully.")
        return redirect('employee_list')

    return render(request, 'confirm_delete.html', {
        'object_name': f"Employee: {employee.full_name} ({employee.emp_id})",
        'allow_deactivate': True,
        'cancel_url': 'employee_list'
    })

@login_required
def employee_self_edit_view(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "No employee record associated with this account.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = EmployeeSelfUpdateForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            log_action(request, "Self Profile Updated", f"Employee {employee.emp_id} updated personal contact details.")
            messages.success(request, "Your personal details have been updated successfully!")
            return redirect('profile')
    else:
        form = EmployeeSelfUpdateForm(instance=employee)

    return render(request, 'employee_self_edit.html', {'form': form, 'employee': employee})
