from django.core.management.base import BaseCommand

from d11.models.aleph import ImportFromAleph
from d11.services.aleph_transport import AlephTransportImportService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('imports_ids', type=int, nargs='*')

    def handle(self, *args, **options):
        for imports_instance in ImportFromAleph.objects.filter(id__in=options['imports_ids']):
            AlephTransportImportService(imports_instance).docs_import()
