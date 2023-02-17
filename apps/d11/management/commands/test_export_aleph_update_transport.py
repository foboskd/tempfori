from django.core.management.base import BaseCommand

from d11.models.aleph import ExportToAleph
from d11.services.aleph_transport import AlephTransportExportService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('exports_ids', type=int, nargs='*')

    def handle(self, *args, **options):
        for export_instance in ExportToAleph.objects.filter(id__in=options['exports_ids']):
            AlephTransportExportService(export_instance).docs_update()
