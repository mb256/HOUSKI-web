from django import forms
from .models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone']
        labels = {
            'first_name': 'Jméno',
            'last_name':  'Příjmení',
            'email':      'E-mail',
            'telephone':  'Telefon',
        }
