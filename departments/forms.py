from django import forms
from departments.models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_code', 'name', 'description']
        widgets = {
            'department_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. IT, HR, FIN'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Information Technology'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description of the department...'}),
        }
