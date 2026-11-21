from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from departments.models import Department
from departments.forms import DepartmentForm
from accounts.decorators import hr_or_admin_required, log_action

@login_required
@hr_or_admin_required
def department_list_view(request):
    search_query = request.GET.get('search', '').strip()
    departments = Department.objects.annotate(total_emp=Count('employees')).order_by('name')

    if search_query:
        departments = departments.filter(name__icontains=search_query) | departments.filter(department_code__icontains=search_query)

    return render(request, 'department_list.html', {
        'departments': departments,
        'search_query': search_query,
    })

@login_required
@hr_or_admin_required
def department_add_view(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            dept = form.save()
            log_action(request, "Department Created", f"Created department {dept.name} ({dept.department_code})")
            messages.success(request, f"Department '{dept.name}' created successfully!")
            return redirect('department_list')
    else:
        form = DepartmentForm()

    return render(request, 'department_add.html', {'form': form, 'action_title': 'Add New Department'})

@login_required
@hr_or_admin_required
def department_edit_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            dept = form.save()
            log_action(request, "Department Updated", f"Updated department {dept.name}")
            messages.success(request, f"Department '{dept.name}' updated successfully!")
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=dept)

    return render(request, 'department_add.html', {'form': form, 'dept': dept, 'action_title': 'Edit Department'})

@login_required
@hr_or_admin_required
def department_delete_view(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        if dept.employees.count() > 0:
            messages.error(request, f"Cannot delete department '{dept.name}' because it currently has assigned employees. Reassign employees first.")
        else:
            name = dept.name
            dept.delete()
            log_action(request, "Department Deleted", f"Deleted department {name}")
            messages.success(request, f"Department '{name}' was deleted successfully.")
        return redirect('department_list')

    return render(request, 'confirm_delete.html', {
        'object_name': f"Department: {dept.name}",
        'cancel_url': 'department_list'
    })
