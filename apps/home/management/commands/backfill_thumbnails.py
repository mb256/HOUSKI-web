from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.board.models import BoardImage
from apps.home.models import PictureOfWeek, make_thumbnail


class Command(BaseCommand):
    help = 'Generates thumbnails for existing board/picture-of-week images that are missing one.'

    MODELS = [BoardImage, PictureOfWeek]

    def handle(self, *args, **kwargs):
        total = 0
        for model in self.MODELS:
            qs = model.objects.filter(Q(thumbnail='') | Q(thumbnail__isnull=True))
            for obj in qs:
                if not obj.image:
                    continue
                thumb_name = make_thumbnail(obj.image)
                model.objects.filter(pk=obj.pk).update(thumbnail=thumb_name)
                total += 1
        self.stdout.write(self.style.SUCCESS(f'{total} miniatur vytvořeno.'))

