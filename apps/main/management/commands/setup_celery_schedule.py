from django.core.management import call_command
from django.core.management.base import BaseCommand

from django_celery_beat.models import PeriodicTasks


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        if not PeriodicTasks.objects.exists() or options['force']:
            call_command('loaddata', 'celery_schedule')
