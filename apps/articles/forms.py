from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['headline', 'text', 'categories', 'cover_image']
        labels = {
            'headline': 'Nadpis', 'text': 'Text článku', 'categories': 'Kategorie',
            'cover_image': 'Titulní obrázek (nepovinné, jinak se použije první obrázek z textu)',
        }
        widgets = {
            'text': SummernoteWidget(),
            'categories': forms.CheckboxSelectMultiple(),
        }
