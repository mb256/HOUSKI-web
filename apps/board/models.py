from django.db import models
from django.conf import settings
from django_summernote.fields import SummernoteTextField
from apps.home.models import compress_image, make_thumbnail   # reuse helper


class BoardPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, verbose_name='autor')
    headline = models.CharField('nadpis', max_length=200, blank=True)
    text = SummernoteTextField('text')
    created_at = models.DateTimeField('vytvořeno', auto_now_add=True)
    updated_at = models.DateTimeField('aktualizováno', auto_now=True)

    class Meta:
        verbose_name = 'příspěvek'
        verbose_name_plural = 'příspěvky'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.headline or f'Příspěvek #{self.pk}'


class BoardImage(models.Model):
    post = models.ForeignKey(BoardPost, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='board/')
    thumbnail = models.ImageField(upload_to='board/', null=True, blank=True, editable=False)
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
                BoardImage.objects.filter(pk=self.pk).update(image=new_name)
                self.image.name = new_name
            thumb_name = make_thumbnail(self.image)
            BoardImage.objects.filter(pk=self.pk).update(thumbnail=thumb_name)
            self.thumbnail.name = thumb_name
