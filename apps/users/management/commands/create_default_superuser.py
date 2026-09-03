from django.core.management.base import BaseCommand
from apps.users.models import User


class Command(BaseCommand):
    help = 'Creates default superuser brouk if not exists'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='brouk').exists():
            user = User.objects.create_superuser('brouk', '', 'Admin1234#')
            user.must_change_password = False
            user.save()
            self.stdout.write(self.style.SUCCESS('Superuser brouk created.'))
        else:
            self.stdout.write('Superuser brouk already exists.')
