from django.core.management import call_command
from django.core.management.base import BaseCommand

from d11.models import Ref


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true')

    def handle(self, *args, **options):
        if not Ref.objects.exists() or options['force']:
            call_command('loaddata', 'ref')
