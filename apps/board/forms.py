from django import forms
from django.forms import modelformset_factory
from django_summernote.widgets import SummernoteWidget
from .models import BoardPost, BoardImage


class BoardPostForm(forms.ModelForm):
    class Meta:
        model = BoardPost
        fields = ['headline', 'text']
        labels = {'headline': 'Nadpis (nepovinný)', 'text': 'Text příspěvku'}
        widgets = {
            # No 'picture' button: board images are attached separately via
            # BoardImage below the text, not embedded inline in Summernote.
            'text': SummernoteWidget(attrs={'summernote': {
                'toolbar': [
                    ['style', ['bold', 'italic', 'underline', 'clear']],
                    ['para', ['ul', 'ol', 'paragraph']],
                    ['insert', ['link']],
                    ['view', ['fullscreen']],
                ],
            }}),
        }


BoardImageFormSet = modelformset_factory(
    BoardImage,
    fields=['image'],
    extra=5,
    max_num=5,
    can_delete=True,
)
