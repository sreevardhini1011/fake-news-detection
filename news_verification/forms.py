from django import forms
from .models import NewsSubmission

class NewsSubmissionForm(forms.ModelForm):
    class Meta:
        model = NewsSubmission
        fields = ['submission_type', 'title', 'content', 'url']
        widgets = {
            'submission_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter news title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Paste news content here'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/news-article'}),
        }
