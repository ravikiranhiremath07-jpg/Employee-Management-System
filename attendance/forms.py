from django import forms
from attendance.models import Attendance
from employees.models import Employee
from django.utils import timezone

class AttendanceMarkForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'date', 'status', 'check_in_time', 'check_out_time', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'check_in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and 'date' not in self.initial:
            self.initial['date'] = timezone.localdate()

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        att_date = cleaned_data.get('date')

        if employee and att_date:
            qs = Attendance.objects.filter(employee=employee, date=att_date)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f"Attendance for {employee.full_name} ({employee.emp_id}) on {att_date} has already been recorded! Please edit the existing entry."
                )
        return cleaned_data
