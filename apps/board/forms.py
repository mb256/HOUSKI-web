from django import forms
from django.forms import modelformset_factory
from django_summernote.widgets import SummernoteWidget
from .models import BoardPost, BoardImage


class BoardPostForm(forms.ModelForm):
    class Meta:
        model = BoardPost
        fields = ['headline', 'text']
        labels = {'headline': 'Nadpis (nepovinný)', 'text': 'Text příspěvku'}
        widgets = {'text': SummernoteWidget()}


BoardImageFormSet = modelformset_factory(
    BoardImage,
    fields=['image'],
    extra=5,
    max_num=5,
    can_delete=True,
)
