from django.core.management.base import BaseCommand

from d11.tasks import d11_import_from_aleph


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-a', '--async', dest='is_async', action='store_true')

    def handle(self, *args, **options):
        task_fnc = d11_import_from_aleph
        if options['is_async']:
            task_fnc = task_fnc.delay
        task_fnc()
