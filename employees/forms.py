from django import forms
from django.contrib.auth.models import User
from employees.models import Employee
from accounts.models import UserProfile
from departments.models import Department
from leaves.models import LeaveBalance
from datetime import date

class EmployeeAddForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Login Username'})
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Initial Password'}),
        help_text="Provide a strong initial password for the employee account."
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='EMPLOYEE',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Employee
        fields = [
            'emp_id', 'first_name', 'last_name', 'email', 'phone', 'gender',
            'date_of_birth', 'address', 'profile_photo', 'joining_date',
            'department', 'designation', 'employment_status', 'emergency_contact'
        ]
        widgets = {
            'emp_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EMP001'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name & Phone'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_emp_id(self):
        emp_id = self.cleaned_data['emp_id'].strip().upper()
        if Employee.objects.filter(emp_id=emp_id).exists():
            raise forms.ValidationError("An employee with this Employee ID already exists.")
        return emp_id

    def save(self, commit=True):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        role = self.cleaned_data['role']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        email = self.cleaned_data['email']

        # Create auth user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        # Create profile
        UserProfile.objects.create(user=user, role=role)

        employee = super().save(commit=False)
        employee.user = user
        employee.emp_id = self.cleaned_data['emp_id']

        if commit:
            employee.save()
            # Initialize current year leave balance
            LeaveBalance.objects.get_or_create(
                employee=employee,
                year=date.today().year,
                defaults={'casual_leave': 12, 'sick_leave': 10, 'earned_leave': 15}
            )
        return employee


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'emp_id', 'first_name', 'last_name', 'email', 'phone', 'gender',
            'date_of_birth', 'address', 'profile_photo', 'joining_date',
            'department', 'designation', 'employment_status', 'emergency_contact'
        ]
        widgets = {
            'emp_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EmployeeSelfUpdateForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['phone', 'address', 'emergency_contact', 'profile_photo']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
