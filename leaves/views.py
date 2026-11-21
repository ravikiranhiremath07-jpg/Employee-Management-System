from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date
from django.db.models import Q
from django.contrib.auth.models import User

from leaves.models import LeaveApplication, LeaveBalance
from leaves.forms import LeaveApplyForm, LeaveReviewForm
from employees.models import Employee
from accounts.models import Notification
from accounts.decorators import hr_or_admin_required, log_action

@login_required
@hr_or_admin_required
def leave_list_view(request):
    status_filter = request.GET.get('status', '').strip()
    type_filter = request.GET.get('leave_type', '').strip()
    search_query = request.GET.get('search', '').strip()

    leaves = LeaveApplication.objects.select_related('employee', 'employee__department', 'reviewed_by').order_by('-applied_on')

    if status_filter:
        leaves = leaves.filter(status=status_filter)

    if type_filter:
        leaves = leaves.filter(leave_type=type_filter)

    if search_query:
        leaves = leaves.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__emp_id__icontains=search_query)
        )

    pending_count = LeaveApplication.objects.filter(status='PENDING').count()
    approved_count = LeaveApplication.objects.filter(status='APPROVED').count()
    rejected_count = LeaveApplication.objects.filter(status='REJECTED').count()

    paginator = Paginator(leaves, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'leave_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    })

@login_required
def leave_apply_view(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Only employees with active profiles can apply for leave.")
        return redirect('dashboard')

    year = date.today().year
    balance, _ = LeaveBalance.objects.get_or_create(
        employee=employee, year=year,
        defaults={'casual_leave': 12, 'sick_leave': 10, 'earned_leave': 15}
    )

    if request.method == 'POST':
        form = LeaveApplyForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = employee
            total_days = (leave.end_date - leave.start_date).days + 1
            leave.total_days = total_days

            # Check balance
            if leave.leave_type == 'CASUAL' and total_days > balance.casual_leave:
                messages.error(request, f"Insufficient Casual Leave balance! You have {balance.casual_leave} days remaining.")
                return render(request, 'leave_apply.html', {'form': form, 'balance': balance, 'employee': employee})
            elif leave.leave_type == 'SICK' and total_days > balance.sick_leave:
                messages.error(request, f"Insufficient Sick Leave balance! You have {balance.sick_leave} days remaining.")
                return render(request, 'leave_apply.html', {'form': form, 'balance': balance, 'employee': employee})
            elif leave.leave_type == 'EARNED' and total_days > balance.earned_leave:
                messages.error(request, f"Insufficient Earned Leave balance! You have {balance.earned_leave} days remaining.")
                return render(request, 'leave_apply.html', {'form': form, 'balance': balance, 'employee': employee})

            leave.save()
            log_action(request, "Leave Application Submitted", f"Leave application #{leave.pk} submitted by {employee.emp_id}")

            # Notify Admin and HR users
            admin_users = User.objects.filter(Q(is_superuser=True) | Q(profile__role__in=['ADMIN', 'HR']))
            for u in admin_users:
                Notification.objects.create(
                    recipient=u,
                    title="New Leave Application",
                    message=f"{employee.full_name} ({employee.emp_id}) applied for {leave.get_leave_type_display()} ({total_days} days).",
                    link=f"/leaves/{leave.pk}/review/"
                )

            messages.success(request, "Your leave application has been submitted successfully and is pending review.")
            return redirect('my_leaves')
    else:
        form = LeaveApplyForm()

    return render(request, 'leave_apply.html', {'form': form, 'balance': balance, 'employee': employee})

@login_required
@hr_or_admin_required
def leave_review_view(request, pk):
    leave = get_object_or_404(LeaveApplication.objects.select_related('employee'), pk=pk)
    balance, _ = LeaveBalance.objects.get_or_create(employee=leave.employee, year=leave.start_date.year)
    prev_status = leave.status

    if request.method == 'POST':
        form = LeaveReviewForm(request.POST, instance=leave)
        if form.is_valid():
            reviewed_leave = form.save(commit=False)
            reviewed_leave.reviewed_by = request.user
            reviewed_leave.reviewed_on = timezone.now()

            # If approving and previously was not approved, deduct balance
            if reviewed_leave.status == 'APPROVED' and prev_status != 'APPROVED':
                if reviewed_leave.leave_type == 'CASUAL':
                    balance.casual_leave = max(0, balance.casual_leave - reviewed_leave.total_days)
                elif reviewed_leave.leave_type == 'SICK':
                    balance.sick_leave = max(0, balance.sick_leave - reviewed_leave.total_days)
                elif reviewed_leave.leave_type == 'EARNED':
                    balance.earned_leave = max(0, balance.earned_leave - reviewed_leave.total_days)
                balance.save()

            # If changing from approved to rejected, refund balance
            elif reviewed_leave.status == 'REJECTED' and prev_status == 'APPROVED':
                if reviewed_leave.leave_type == 'CASUAL':
                    balance.casual_leave += reviewed_leave.total_days
                elif reviewed_leave.leave_type == 'SICK':
                    balance.sick_leave += reviewed_leave.total_days
                elif reviewed_leave.leave_type == 'EARNED':
                    balance.earned_leave += reviewed_leave.total_days
                balance.save()

            reviewed_leave.save()

            # Notify the employee
            Notification.objects.create(
                recipient=leave.employee.user,
                title=f"Leave Application {reviewed_leave.status.title()}",
                message=f"Your leave application for {leave.start_date} to {leave.end_date} has been {reviewed_leave.status.lower()} by {request.user.username}.",
                link="/leaves/my-history/"
            )

            log_action(request, f"Leave {reviewed_leave.status.title()}", f"Leave #{leave.id} for {leave.employee.emp_id} set to {reviewed_leave.status}")
            messages.success(request, f"Leave application #{leave.pk} has been {reviewed_leave.status.lower()}.")
            return redirect('leave_list')
    else:
        form = LeaveReviewForm(instance=leave)

    return render(request, 'leave_review.html', {
        'form': form,
        'leave': leave,
        'balance': balance,
    })

@login_required
def my_leaves_view(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "No employee record associated with your account.")
        return redirect('dashboard')

    year = date.today().year
    balance, _ = LeaveBalance.objects.get_or_create(
        employee=employee, year=year,
        defaults={'casual_leave': 12, 'sick_leave': 10, 'earned_leave': 15}
    )

    leaves = LeaveApplication.objects.filter(employee=employee).order_by('-applied_on')
    paginator = Paginator(leaves, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'leave_my.html', {
        'page_obj': page_obj,
        'employee': employee,
        'balance': balance,
    })
