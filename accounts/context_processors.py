from accounts.models import Notification
from employees.models import Employee

def auth_roles(request):
    """
    Context processor to make user role and profile globally accessible in all templates.
    """
    if not request.user.is_authenticated:
        return {
            'user_role': 'GUEST',
            'is_admin_user': False,
            'is_hr_user': False,
            'is_employee_user': False,
            'current_employee': None,
            'unread_notifications_count': 0,
            'recent_notifications': [],
        }

    role = 'EMPLOYEE'
    if request.user.is_superuser:
        role = 'ADMIN'
    elif hasattr(request.user, 'profile'):
        role = request.user.profile.role

    employee = None
    try:
        employee = request.user.employee_profile
    except Exception:
        employee = None

    unread_count = 0
    recent_notifs = []
    try:
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent_notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    except Exception:
        pass

    return {
        'user_role': role,
        'is_admin_user': (role == 'ADMIN'),
        'is_hr_user': (role == 'HR'),
        'is_employee_user': (role == 'EMPLOYEE'),
        'current_employee': employee,
        'unread_notifications_count': unread_count,
        'recent_notifications': recent_notifs,
    }
