from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    ROLE_CHOICES = [
        ('predseda',   'Předseda'),
        ('tajemnik',   'Tajemník'),
        ('pokladnik',  'Pokladník'),
        ('clen',       'Člen'),
        ('instruktor', 'Instruktor'),
    ]
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    class Meta:
        verbose_name = 'role'
        verbose_name_plural = 'role'

    def __str__(self) -> str:
        return self.get_name_display()


class User(AbstractUser):
    telephone = models.CharField('telefon', max_length=20, blank=True)
    roles = models.ManyToManyField(Role, blank=True, verbose_name='role')
    must_change_password = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'uživatel'
        verbose_name_plural = 'uživatelé'

    def __str__(self) -> str:
        return self.username
