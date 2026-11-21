from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta, time
from decimal import Decimal
import random

from accounts.models import UserProfile, Notification, AuditLog
from departments.models import Department
from employees.models import Employee
from attendance.models import Attendance
from leaves.models import LeaveBalance, LeaveApplication
from payroll.models import Salary

class Command(BaseCommand):
    help = "Populate database with rich sample data for demonstrative testing."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Populating sample data for Employee Management System..."))

        # 1. Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ems.company.com',
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'ADMIN'})
        self.stdout.write(self.style.SUCCESS("✓ Admin user ready: admin / admin123"))

        # 2. Create HR User
        hr_user, created = User.objects.get_or_create(
            username='hrmanager',
            defaults={
                'email': 'hr@ems.company.com',
                'first_name': 'Ananya',
                'last_name': 'Sharma',
                'is_staff': True,
            }
        )
        if created:
            hr_user.set_password('hr12345')
            hr_user.save()
        UserProfile.objects.get_or_create(user=hr_user, defaults={'role': 'HR'})
        self.stdout.write(self.style.SUCCESS("✓ HR Manager ready: hrmanager / hr12345"))

        # 3. Create Departments
        departments_data = [
            {'code': 'ENG', 'name': 'Engineering & Technology', 'desc': 'Software development, cloud systems, and platform engineering.'},
            {'code': 'HR', 'name': 'Human Resources', 'desc': 'Talent acquisition, employee welfare, performance and culture.'},
            {'code': 'FIN', 'name': 'Finance & Accounts', 'desc': 'Financial reporting, auditing, payroll and financial compliance.'},
            {'code': 'MKT', 'name': 'Marketing & Design', 'desc': 'Brand strategy, UI/UX design, growth and digital campaigns.'},
            {'code': 'OPS', 'name': 'Operations & Support', 'desc': 'Business operations, IT support, logistics and infrastructure.'},
        ]

        depts = {}
        for d in departments_data:
            dept, _ = Department.objects.get_or_create(
                department_code=d['code'],
                defaults={'name': d['name'], 'description': d['desc']}
            )
            depts[d['code']] = dept
        self.stdout.write(self.style.SUCCESS(f"✓ Created/Verified {len(depts)} Departments."))

        # 4. Create Sample Employees
        employees_data = [
            {
                'username': 'emp_rahul',
                'password': 'emp12345',
                'emp_id': 'EMP001',
                'first_name': 'Rahul',
                'last_name': 'Verma',
                'email': 'rahul.verma@ems.company.com',
                'phone': '+91 98765 43210',
                'gender': 'Male',
                'dob': date(1995, 4, 15),
                'joining': date(2022, 3, 1),
                'dept': depts['ENG'],
                'designation': 'Senior Software Engineer',
                'basic': Decimal('85000.00'),
                'allowances': Decimal('15000.00'),
                'deductions': Decimal('7500.00'),
            },
            {
                'username': 'emp_priya',
                'password': 'emp12345',
                'emp_id': 'EMP002',
                'first_name': 'Priya',
                'last_name': 'Nair',
                'email': 'priya.nair@ems.company.com',
                'phone': '+91 98765 43211',
                'gender': 'Female',
                'dob': date(1997, 8, 22),
                'joining': date(2023, 1, 10),
                'dept': depts['MKT'],
                'designation': 'Lead UI/UX Designer',
                'basic': Decimal('75000.00'),
                'allowances': Decimal('12000.00'),
                'deductions': Decimal('6000.00'),
            },
            {
                'username': 'emp_amit',
                'password': 'emp12345',
                'emp_id': 'EMP003',
                'first_name': 'Amit',
                'last_name': 'Patel',
                'email': 'amit.patel@ems.company.com',
                'phone': '+91 98765 43212',
                'gender': 'Male',
                'dob': date(1993, 11, 5),
                'joining': date(2021, 7, 15),
                'dept': depts['FIN'],
                'designation': 'Senior Financial Analyst',
                'basic': Decimal('80000.00'),
                'allowances': Decimal('14000.00'),
                'deductions': Decimal('7000.00'),
            },
            {
                'username': 'emp_neha',
                'password': 'emp12345',
                'emp_id': 'EMP004',
                'first_name': 'Neha',
                'last_name': 'Kapoor',
                'email': 'neha.kapoor@ems.company.com',
                'phone': '+91 98765 43213',
                'gender': 'Female',
                'dob': date(1998, 2, 18),
                'joining': date(2023, 6, 1),
                'dept': depts['HR'],
                'designation': 'HR Executive & Recruiter',
                'basic': Decimal('55000.00'),
                'allowances': Decimal('9000.00'),
                'deductions': Decimal('4500.00'),
            },
            {
                'username': 'emp_vikram',
                'password': 'emp12345',
                'emp_id': 'EMP005',
                'first_name': 'Vikram',
                'last_name': 'Singh',
                'email': 'vikram.singh@ems.company.com',
                'phone': '+91 98765 43214',
                'gender': 'Male',
                'dob': date(1994, 9, 30),
                'joining': date(2022, 11, 20),
                'dept': depts['OPS'],
                'designation': 'DevOps & Cloud Engineer',
                'basic': Decimal('90000.00'),
                'allowances': Decimal('16000.00'),
                'deductions': Decimal('8000.00'),
            },
        ]

        created_employees = []
        today = timezone.localdate()
        current_year = today.year

        for item in employees_data:
            user, u_created = User.objects.get_or_create(
                username=item['username'],
                defaults={
                    'email': item['email'],
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                }
            )
            if u_created:
                user.set_password(item['password'])
                user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'EMPLOYEE'})

            emp, e_created = Employee.objects.get_or_create(
                emp_id=item['emp_id'],
                defaults={
                    'user': user,
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                    'email': item['email'],
                    'phone': item['phone'],
                    'gender': item['gender'],
                    'date_of_birth': item['dob'],
                    'address': f"Plot {random.randint(10, 200)}, Tech Park Road, Sector {random.randint(1, 15)}",
                    'joining_date': item['joining'],
                    'department': item['dept'],
                    'designation': item['designation'],
                    'employment_status': 'ACTIVE',
                    'emergency_contact': f"Parent / Spouse: +91 98765 000{random.randint(10, 99)}",
                }
            )
            created_employees.append((emp, item))

            # Initialize Leave Balances
            LeaveBalance.objects.get_or_create(
                employee=emp, year=current_year,
                defaults={'casual_leave': 12, 'sick_leave': 10, 'earned_leave': 15}
            )

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(created_employees)} Employee accounts (emp_rahul .. emp_vikram / emp12345)."))

        # 5. Populate Realistic Attendance Records for Past 20 Working Days
        self.stdout.write("Generating attendance records...")
        for emp, _ in created_employees:
            for day_offset in range(20, -1, -1):
                att_date = today - timedelta(days=day_offset)
                # Skip Sundays
                if att_date.weekday() == 6:
                    continue

                if Attendance.objects.filter(employee=emp, date=att_date).exists():
                    continue

                # Realistic distribution: 85% Present, 5% Half-day, 5% Leave, 5% Absent
                r = random.random()
                if r < 0.85:
                    status = 'PRESENT'
                    in_time = time(random.randint(8, 9), random.randint(15, 59))
                    out_time = time(random.randint(17, 18), random.randint(30, 59))
                    notes = 'Regular working day'
                elif r < 0.90:
                    status = 'HALF_DAY'
                    in_time = time(9, 10)
                    out_time = time(13, 30)
                    notes = 'Approved half day afternoon off'
                elif r < 0.95:
                    status = 'ON_LEAVE'
                    in_time = None
                    out_time = None
                    notes = 'Pre-approved leave'
                else:
                    status = 'ABSENT'
                    in_time = None
                    out_time = None
                    notes = 'Unplanned absence'

                Attendance.objects.create(
                    employee=emp,
                    date=att_date,
                    status=status,
                    check_in_time=in_time,
                    check_out_time=out_time,
                    notes=notes
                )

        # 6. Create Sample Leave Applications
        self.stdout.write("Generating sample leave applications...")
        emp_rahul = created_employees[0][0]
        emp_priya = created_employees[1][0]
        emp_amit = created_employees[2][0]

        # Approved leave
        if not LeaveApplication.objects.filter(employee=emp_rahul).exists():
            LeaveApplication.objects.create(
                employee=emp_rahul,
                leave_type='CASUAL',
                start_date=today - timedelta(days=10),
                end_date=today - timedelta(days=9),
                total_days=2,
                reason="Attending family function out of station.",
                status='APPROVED',
                reviewed_by=hr_user,
                review_comment="Approved. Handover tasks to team.",
                reviewed_on=timezone.now() - timedelta(days=12)
            )

        # Pending leave
        if not LeaveApplication.objects.filter(employee=emp_priya).exists():
            LeaveApplication.objects.create(
                employee=emp_priya,
                leave_type='SICK',
                start_date=today + timedelta(days=2),
                end_date=today + timedelta(days=3),
                total_days=2,
                reason="Medical appointment and rest as advised by physician.",
                status='PENDING'
            )

        # Rejected leave
        if not LeaveApplication.objects.filter(employee=emp_amit).exists():
            LeaveApplication.objects.create(
                employee=emp_amit,
                leave_type='EARNED',
                start_date=today + timedelta(days=15),
                end_date=today + timedelta(days=25),
                total_days=11,
                reason="Extended vacation during quarter-end.",
                status='REJECTED',
                reviewed_by=admin_user,
                review_comment="Rejected due to pending quarterly financial audit closing.",
                reviewed_on=timezone.now() - timedelta(days=1)
            )

        # 7. Create Salary Records for Past 3 Months
        self.stdout.write("Generating payroll salary statements...")
        for emp, info in created_employees:
            for m_offset in [2, 1, 0]:
                target_month = today.month - m_offset
                target_year = today.year
                if target_month <= 0:
                    target_month += 12
                    target_year -= 1

                if not Salary.objects.filter(employee=emp, month=target_month, year=target_year).exists():
                    p_status = 'PAID' if m_offset > 0 else 'PENDING'
                    pay_date = date(target_year, target_month, 28) if p_status == 'PAID' else None
                    Salary.objects.create(
                        employee=emp,
                        month=target_month,
                        year=target_year,
                        basic_salary=info['basic'],
                        allowances=info['allowances'],
                        deductions=info['deductions'],
                        payment_date=pay_date,
                        payment_status=p_status,
                        notes=f"Monthly salary transfer for {target_month}/{target_year}"
                    )

        # 8. Notifications
        for emp, _ in created_employees:
            Notification.objects.get_or_create(
                recipient=emp.user,
                title="Welcome to EMS Portal",
                defaults={
                    'message': f"Welcome {emp.first_name}! You can view your attendance, salary slips and apply for leaves directly from this dashboard.",
                    'is_read': False,
                    'link': '/profile/'
                }
            )

        # 9. Audit Logs
        AuditLog.objects.create(
            user=admin_user,
            action="System Initialized",
            details="Populated sample database with employees, departments, payroll, and attendance records.",
            ip_address="127.0.0.1"
        )

        self.stdout.write(self.style.SUCCESS("\n🎉 Sample data successfully seeded into SQLite database!"))
        self.stdout.write(self.style.SUCCESS("Available Demo Logins:"))
        self.stdout.write(" - Admin:      username: admin      | password: admin123")
        self.stdout.write(" - HR Manager: username: hrmanager  | password: hr12345")
        self.stdout.write(" - Employees:  username: emp_rahul  | password: emp12345 (also emp_priya, emp_amit, emp_neha, emp_vikram)")
