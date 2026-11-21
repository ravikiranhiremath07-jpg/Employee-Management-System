from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import AuditLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(request, action, details=""):
    try:
        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)
        AuditLog.objects.create(
            user=user,
            action=action,
            details=details,
            ip_address=ip
        )
    except Exception:
        pass

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied: Administrator permissions required.")
        return redirect('dashboard')
    return wrapper

def hr_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.role in ['ADMIN', 'HR']):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied: HR Manager or Administrator permissions required.")
        return redirect('dashboard')
    return wrapper
