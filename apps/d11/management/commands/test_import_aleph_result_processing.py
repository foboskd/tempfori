from django.core.management.base import BaseCommand

from d11.models.aleph import ImportFromAleph
from d11.services.aleph_import import AlephImportDocsService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('imports_ids', type=int, nargs='*')

    def handle(self, *args, **options):
        for import_instance in ImportFromAleph.objects.filter(id__in=options['imports_ids']):
            AlephImportDocsService(import_instance).result_file_process()
