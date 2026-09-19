from django.db import models
from django.conf import settings
from django.urls import reverse
from django_summernote.fields import SummernoteTextField
from apps.home.models import compress_image, make_thumbnail


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('climbing',     'Lezení'),
        ('mountains',    'Hory'),
        ('skialpinism',  'Skialpinismus'),
        ('trekking',     'Trekking'),
        ('other_sport',  'Jiný sport'),
        ('kids',         'Děti'),
        ('pub',          'Hospoda'),
    ]
    slug = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'kategorie'
        verbose_name_plural = 'kategorie'

    def __str__(self) -> str:
        return self.name


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    headline = models.CharField('nadpis', max_length=300)
    text = SummernoteTextField('text')
    categories = models.ManyToManyField(Category, blank=True, verbose_name='kategorie')
    created_at = models.DateTimeField('vytvořeno', auto_now_add=True)
    updated_at = models.DateTimeField('aktualizováno', auto_now=True)

    class Meta:
        verbose_name = 'článek'
        verbose_name_plural = 'články'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.headline

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'pk': self.pk})


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='articles/')
    thumbnail = models.ImageField(upload_to='articles/', null=True, blank=True, editable=False)
    caption = models.CharField('popisek', max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    @property
    def thumb_url(self):
        return self.thumbnail.url if self.thumbnail else self.image.url

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            new_name = compress_image(self.image)
            if new_name:
                ArticleImage.objects.filter(pk=self.pk).update(image=new_name)
                self.image.name = new_name
            thumb_name = make_thumbnail(self.image)
            ArticleImage.objects.filter(pk=self.pk).update(thumbnail=thumb_name)
            self.thumbnail.name = thumb_name
