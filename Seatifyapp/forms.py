from django import forms
from .models import Branch, Semester, SeatingArrangement

class SeatingArrangementForm(forms.ModelForm):
    class Meta:
        model = SeatingArrangement
        fields = ['branch', 'semester', 'total_strength', 'absentees', 'rows', 'columns', 'start_date', 'end_date']

        widgets = {
            'absentees': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter branch name'}),
        }

class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter semester name'}),
        }
