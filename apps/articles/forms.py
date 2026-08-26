from django import forms
from django.forms import modelformset_factory
from django_summernote.widgets import SummernoteWidget
from .models import Article, ArticleImage


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['headline', 'text', 'categories']
        labels = {'headline': 'Nadpis', 'text': 'Text článku', 'categories': 'Kategorie'}
        widgets = {
            'text': SummernoteWidget(),
            'categories': forms.CheckboxSelectMultiple(),
        }


ArticleImageFormSet = modelformset_factory(
    ArticleImage,
    fields=['image', 'caption'],
    extra=10,
    max_num=10,
    can_delete=True,
)
