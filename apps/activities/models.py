from django.db import models
from django.conf import settings
from apps.home.fields import SummernoteTextField


class Activity(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    name = models.CharField('název', max_length=200)
    start_date = models.DateField('datum začátku')
    end_date = models.DateField('datum konce', null=True, blank=True)
    location = models.CharField('místo', max_length=200)
    description = SummernoteTextField('popis')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'aktivita'
        verbose_name_plural = 'aktivity'
        ordering = ['start_date']

    def __str__(self) -> str:
        return self.name
