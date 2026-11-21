from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import UserProfile, AuditLog, Notification
from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance
from leaves.models import LeaveApplication, LeaveBalance
from payroll.models import Salary
from datetime import date
from decimal import Decimal

class EMSTestSuite(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Admin
        self.admin_user = User.objects.create_superuser('test_admin', 'admin@test.com', 'pass123')
        UserProfile.objects.create(user=self.admin_user, role='ADMIN')

        # Create HR
        self.hr_user = User.objects.create_user('test_hr', 'hr@test.com', 'pass123')
        UserProfile.objects.create(user=self.hr_user, role='HR')

        # Create Employee User
        self.emp_user = User.objects.create_user('test_emp', 'emp@test.com', 'pass123')
        UserProfile.objects.create(user=self.emp_user, role='EMPLOYEE')

        # Department
        self.dept = Department.objects.create(department_code='IT', name='Information Technology')

        # Employee Profile
        self.employee = Employee.objects.create(
            user=self.emp_user,
            emp_id='EMP999',
            first_name='Test',
            last_name='Worker',
            email='emp@test.com',
            phone='9999999999',
            gender='Male',
            date_of_birth=date(1996, 1, 1),
            joining_date=date(2023, 1, 1),
            department=self.dept,
            designation='Developer',
            employment_status='ACTIVE'
        )

        # Leave balance
        self.leave_bal = LeaveBalance.objects.create(
            employee=self.employee,
            year=2026,
            casual_leave=12,
            sick_leave=10,
            earned_leave=15
        )

    def test_login_flow(self):
        response = self.client.post('/accounts/login/', {'username': 'test_admin', 'password': 'pass123'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_unauthorized_access_redirects(self):
        # Unauthenticated user visiting employee list should redirect to login
        response = self.client.get('/employees/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_employee_permission_restriction(self):
        # Logged in as Employee attempting to visit employee creation page
        self.client.login(username='test_emp', password='pass123')
        response = self.client.get('/employees/add/')
        # Should be redirected to dashboard because employee lacks HR/Admin permission
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_net_salary_automatic_calculation(self):
        # Formula: Net Salary = Basic + Allowances - Deductions
        salary = Salary.objects.create(
            employee=self.employee,
            month=5,
            year=2026,
            basic_salary=Decimal('50000.00'),
            allowances=Decimal('10000.00'),
            deductions=Decimal('5000.00')
        )
        self.assertEqual(salary.net_salary, Decimal('55000.00'))

    def test_duplicate_attendance_prevention(self):
        att1 = Attendance.objects.create(
            employee=self.employee,
            date=date(2026, 5, 10),
            status='PRESENT'
        )
        # Attempting duplicate should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                employee=self.employee,
                date=date(2026, 5, 10),
                status='ABSENT'
            )

    def test_leave_approval_deducts_balance(self):
        self.client.login(username='test_admin', password='pass123')
        leave = LeaveApplication.objects.create(
            employee=self.employee,
            leave_type='CASUAL',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 2),
            total_days=2,
            reason='Personal work',
            status='PENDING'
        )
        # Review and approve
        response = self.client.post(f'/leaves/{leave.pk}/review/', {
            'status': 'APPROVED',
            'review_comment': 'Granted'
        })
        self.assertEqual(response.status_code, 302)

        # Check balance was deducted from 12 to 10
        self.leave_bal.refresh_from_db()
        self.assertEqual(self.leave_bal.casual_leave, 10)

    def test_csv_export_reports(self):
        self.client.login(username='test_admin', password='pass123')
        resp = self.client.get('/reports/export/employees/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
