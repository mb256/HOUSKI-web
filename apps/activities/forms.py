from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'start_date', 'end_date', 'location', 'description']
        labels = {
            'name': 'Název',
            'start_date': 'Datum začátku',
            'end_date': 'Datum konce',
            'location': 'Místo',
            'description': 'Popis',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': SummernoteWidget(),
        }
