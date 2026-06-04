from django import forms
from .models import UserFeedback, ContentReport

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = UserFeedback
        fields = ['feedback_type', 'user_rating', 'comments']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-select'}),
            'user_rating': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional: Share your thoughts...'}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = ContentReport
        fields = ['report_type', 'description']
        widgets = {
            'report_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please describe the issue...'}),
        }
