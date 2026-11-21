from django import forms
from leaves.models import LeaveApplication, LeaveBalance
from django.utils import timezone

class LeaveApplyForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed reason for leave...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date cannot be earlier than start date.")
            if start_date < timezone.localdate():
                raise forms.ValidationError("Start date cannot be in the past.")

            total_days = (end_date - start_date).days + 1
            cleaned_data['total_days'] = total_days
        return cleaned_data

class LeaveReviewForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ['status', 'review_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'review_comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional review comments or conditions...'}),
        }
