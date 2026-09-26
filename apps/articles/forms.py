from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['headline', 'text', 'categories']
        labels = {'headline': 'Nadpis', 'text': 'Text článku', 'categories': 'Kategorie'}
        widgets = {
            'text': SummernoteWidget(),
            'categories': forms.CheckboxSelectMultiple(),
        }
