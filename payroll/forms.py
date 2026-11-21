from django import forms
from payroll.models import Salary
from employees.models import Employee
from datetime import date

class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = ['employee', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'payment_date', 'payment_status', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_basic_salary'}),
            'allowances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_allowances'}),
            'deductions': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_deductions'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Payment notes, bank ref, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            today = date.today()
            self.initial.setdefault('month', today.month)
            self.initial.setdefault('year', today.year)
            self.initial.setdefault('payment_status', 'PENDING')
            self.initial.setdefault('allowances', 0)
            self.initial.setdefault('deductions', 0)

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        month = cleaned_data.get('month')
        year = cleaned_data.get('year')

        if employee and month and year:
            qs = Salary.objects.filter(employee=employee, month=month, year=year)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f"Salary statement for {employee.full_name} for Month {month}, Year {year} already exists!"
                )
        return cleaned_data
