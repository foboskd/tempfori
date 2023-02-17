from django.core.management.base import BaseCommand

from d11.tasks import d11_export_to_aleph_exist


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=None)
        parser.add_argument('-a', '--async', dest='is_async', action='store_true')

    def handle(self, *args, **options):
        task_fnc = d11_export_to_aleph_exist
        if options['is_async']:
            task_fnc = task_fnc.delay
        task_fnc(docs_count=options['count'], is_updated_after_last_export=True)
