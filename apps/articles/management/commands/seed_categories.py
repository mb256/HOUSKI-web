from django.core.management.base import BaseCommand
from apps.articles.models import Category


class Command(BaseCommand):
    help = 'Seeds the default article categories'

    CATEGORIES = [
        ('climbing', 'Lezení'),
        ('mountains', 'Hory'),
        ('skialpinism', 'Skialpinismus'),
        ('trekking', 'Trekking'),
        ('other_sport', 'Jiný sport'),
        ('kids', 'Děti'),
        ('pub', 'Hospoda'),
    ]

    def handle(self, *args, **kwargs):
        created_count = 0
        for slug, name in self.CATEGORIES:
            _, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'{created_count} kategorií vytvořeno.'))
