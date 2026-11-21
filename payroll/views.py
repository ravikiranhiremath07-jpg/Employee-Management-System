from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from datetime import date

from payroll.models import Salary
from payroll.forms import SalaryForm
from employees.models import Employee
from departments.models import Department
from accounts.decorators import hr_or_admin_required, log_action
from accounts.models import Notification

@login_required
@hr_or_admin_required
def salary_list_view(request):
    month_filter = request.GET.get('month', '').strip()
    year_filter = request.GET.get('year', '').strip()
    status_filter = request.GET.get('status', '').strip()
    dept_filter = request.GET.get('department', '').strip()
    search_query = request.GET.get('search', '').strip()

    salaries = Salary.objects.select_related('employee', 'employee__department').order_by('-year', '-month', 'employee__emp_id')

    if month_filter:
        salaries = salaries.filter(month=month_filter)
    if year_filter:
        salaries = salaries.filter(year=year_filter)
    if status_filter:
        salaries = salaries.filter(payment_status=status_filter)
    if dept_filter:
        salaries = salaries.filter(employee__department_id=dept_filter)
    if search_query:
        salaries = salaries.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__emp_id__icontains=search_query)
        )

    # Aggregations
    total_net = salaries.aggregate(Sum('net_salary'))['net_salary__sum'] or 0
    total_basic = salaries.aggregate(Sum('basic_salary'))['basic_salary__sum'] or 0

    paginator = Paginator(salaries, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    departments = Department.objects.all()
    current_year = date.today().year
    years = range(current_year - 4, current_year + 2)

    return render(request, 'salary_list.html', {
        'page_obj': page_obj,
        'departments': departments,
        'years': years,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'search_query': search_query,
        'total_net': total_net,
        'total_basic': total_basic,
    })

@login_required
@hr_or_admin_required
def salary_add_view(request):
    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            salary = form.save()
            log_action(request, "Salary Created", f"Created salary for {salary.employee.emp_id} ({salary.get_month_display()} {salary.year}) - Net: {salary.net_salary}")

            # Notify employee
            Notification.objects.create(
                recipient=salary.employee.user,
                title="Salary Statement Generated",
                message=f"Your salary statement for {salary.get_month_display()} {salary.year} (Net: ₹{salary.net_salary}) has been published.",
                link=f"/payroll/{salary.pk}/statement/"
            )

            messages.success(request, f"Salary statement for {salary.employee.full_name} created successfully!")
            return redirect('salary_detail', pk=salary.pk)
    else:
        form = SalaryForm()

    return render(request, 'salary_add.html', {'form': form, 'title': 'Create Monthly Salary Record'})

@login_required
@hr_or_admin_required
def salary_edit_view(request, pk):
    salary = get_object_or_404(Salary, pk=pk)
    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            sal = form.save()
            log_action(request, "Salary Updated", f"Updated salary #{sal.pk} for {sal.employee.emp_id}")
            messages.success(request, "Salary statement updated successfully.")
            return redirect('salary_detail', pk=sal.pk)
    else:
        form = SalaryForm(instance=salary)

    return render(request, 'salary_add.html', {'form': form, 'title': 'Edit Salary Record', 'salary': salary})

@login_required
def salary_detail_view(request, pk):
    salary = get_object_or_404(Salary.objects.select_related('employee', 'employee__department'), pk=pk)

    # Permission check: Employee can only view their own salary statement
    user = request.user
    is_staff_or_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'HR'])
    if not is_staff_or_admin:
        if not hasattr(user, 'employee_profile') or user.employee_profile.pk != salary.employee.pk:
            messages.error(request, "Unauthorized: You are only permitted to view your own salary statements.")
            return redirect('dashboard')

    return render(request, 'salary_detail.html', {'salary': salary, 'is_staff_or_admin': is_staff_or_admin})

@login_required
def my_salary_view(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "No employee record associated with your account.")
        return redirect('dashboard')

    salaries = Salary.objects.filter(employee=employee).order_by('-year', '-month')
    paginator = Paginator(salaries, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    total_earned = salaries.filter(payment_status='PAID').aggregate(Sum('net_salary'))['net_salary__sum'] or 0

    return render(request, 'salary_my.html', {
        'page_obj': page_obj,
        'employee': employee,
        'total_earned': total_earned,
    })
