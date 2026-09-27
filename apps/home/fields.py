import bleach
from django import forms
from django.db import models
from django_summernote.settings import ALLOWED_TAGS, STYLES
from django_summernote.widgets import SummernoteWidget

# django-summernote's own SummernoteTextField (django_summernote.fields) runs
# every save through bleach.clean() using a hardcoded attribute allowlist
# (django_summernote/settings.py) that has no entry for <img> - only '*'
# (style/align/title) and 'a' (href). That silently strips the src/alt off
# any inline <img> the editor inserts, so pictures never end up in the saved
# HTML. This mirrors django_summernote.fields but adds the img attributes
# needed for inline pictures to survive.
ATTRIBUTES = {
    '*': ['style', 'align', 'title'],
    'a': ['href'],
    'img': ['src', 'alt', 'width', 'height'],
}


class SummernoteTextFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({'widget': SummernoteWidget()})
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ATTRIBUTES, styles=STYLES)


class SummernoteTextField(models.TextField):
    def formfield(self, **kwargs):
        kwargs.update({'form_class': SummernoteTextFormField})
        return super().formfield(**kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ATTRIBUTES, styles=STYLES)
