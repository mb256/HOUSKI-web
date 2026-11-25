from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.articles.models import Article, Category


class Command(BaseCommand):
    help = 'Replaces the categories of ALL existing articles with a single category.'

    def add_arguments(self, parser):
        parser.add_argument('slug')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, slug, dry_run, **options):
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise CommandError(f'Category with slug "{slug}" does not exist.')

        through = Article.categories.through
        links = [through(article_id=pk, category_id=category.pk)
                 for pk in Article.objects.values_list('pk', flat=True)]
        suffix = ' (dry run)' if dry_run else ''
        if not dry_run:
            # Writes the m2m table directly: no Article.save(), so updated_at is untouched.
            with transaction.atomic():
                through.objects.all().delete()
                through.objects.bulk_create(links)
        self.stdout.write(self.style.SUCCESS(
            f'{len(links)} articles now have only category "{category.name}"{suffix}.'
        ))
