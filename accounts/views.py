from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.db.models import Count, Q

from accounts.forms import LoginForm, UserRoleForm
from accounts.models import UserProfile, Notification, AuditLog
from accounts.decorators import admin_required, hr_or_admin_required, log_action
from employees.models import Employee
from departments.models import Department
from attendance.models import Attendance
from leaves.models import LeaveApplication, LeaveBalance
from payroll.models import Salary

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    log_action(request, "User Login", f"User {user.username} logged in successfully.")
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "This account is inactive. Please contact your system administrator.")
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    log_action(request, "User Logout", f"User {request.user.username} logged out.")
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def dashboard_view(request):
    today = timezone.localdate()
    user = request.user
    role = 'EMPLOYEE'
    if user.is_superuser:
        role = 'ADMIN'
    elif hasattr(user, 'profile'):
        role = user.profile.role

    # Context dictionary
    context = {
        'today': today,
        'role': role,
    }

    if role in ['ADMIN', 'HR']:
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(employment_status='ACTIVE').count()
        total_departments = Department.objects.count()

        today_attendances = Attendance.objects.filter(date=today)
        present_today = today_attendances.filter(status='PRESENT').count()
        absent_today = today_attendances.filter(status='ABSENT').count()
        half_day_today = today_attendances.filter(status='HALF_DAY').count()

        pending_leaves = LeaveApplication.objects.filter(status='PENDING').count()
        recent_employees = Employee.objects.order_by('-created_at')[:5]
        recent_leaves = LeaveApplication.objects.order_by('-applied_on')[:5]

        # Department distribution
        departments = Department.objects.annotate(emp_count=Count('employees')).order_by('-emp_count')
        dept_names = [d.name for d in departments]
        dept_counts = [d.emp_count for d in departments]

        # Monthly joining trends (last 6 months)
        current_year = today.year
        salaries_current_month = Salary.objects.filter(month=today.month, year=current_year).count()

        context.update({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'total_departments': total_departments,
            'present_today': present_today,
            'absent_today': absent_today,
            'half_day_today': half_day_today,
            'pending_leaves': pending_leaves,
            'recent_employees': recent_employees,
            'recent_leaves': recent_leaves,
            'dept_names_json': dept_names,
            'dept_counts_json': dept_counts,
            'salaries_current_month': salaries_current_month,
        })
    else:
        # Employee personal dashboard
        employee = None
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            employee = None

        if employee:
            my_attendances = Attendance.objects.filter(employee=employee)
            total_records = my_attendances.count()
            present_days = my_attendances.filter(status='PRESENT').count()
            half_days = my_attendances.filter(status='HALF_DAY').count()
            attendance_percentage = round(((present_days + 0.5 * half_days) / total_records * 100), 1) if total_records > 0 else 0

            # Today's status
            today_att = my_attendances.filter(date=today).first()

            # Leave Balances
            balance, _ = LeaveBalance.objects.get_or_create(
                employee=employee, year=today.year,
                defaults={'casual_leave': 12, 'sick_leave': 10, 'earned_leave': 15}
            )

            # Recent leaves
            my_recent_leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_on')[:5]
            # Recent salary
            recent_salary = Salary.objects.filter(employee=employee).order_by('-year', '-month').first()

            context.update({
                'employee': employee,
                'total_attendance_records': total_records,
                'attendance_percentage': attendance_percentage,
                'present_days': present_days,
                'today_att': today_att,
                'leave_balance': balance,
                'my_recent_leaves': my_recent_leaves,
                'recent_salary': recent_salary,
            })

    return render(request, 'dashboard.html', context)

@login_required
def profile_view(request):
    user = request.user
    employee = None
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        employee = None

    return render(request, 'profile.html', {'user_obj': user, 'employee': employee})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_action(request, "Password Changed", f"Password updated for user {user.username}")
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error(s) below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    # Mark all as read when visited
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    return redirect('notifications')

@login_required
@admin_required
def user_list_view(request):
    users = User.objects.all().select_related('profile', 'employee_profile').order_by('username')
    return render(request, 'user_list.html', {'users': users})

@login_required
@admin_required
def user_edit_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        role = request.POST.get('role', 'EMPLOYEE')
        is_active = request.POST.get('is_active') == 'on'
        profile.role = role
        profile.save()
        target_user.is_active = is_active
        target_user.save()
        log_action(request, "User Account Updated", f"Updated account {target_user.username} role to {role}")
        messages.success(request, f"User {target_user.username} updated successfully.")
        return redirect('user_list')

    return render(request, 'user_edit.html', {'target_user': target_user, 'profile': profile})
