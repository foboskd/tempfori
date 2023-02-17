from django.core.management.base import BaseCommand

from d11.models.aleph import ExportToAleph, ExportAlephKind
from d11.services.aleph_transport import AlephTransportExportService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('exports_ids', type=int, nargs='*')

    def handle(self, *args, **options):
        for export_instance in ExportToAleph.objects.filter(id__in=options['exports_ids']):
            mthd = 'docs_create_both_cards'
            if export_instance.kind != ExportAlephKind.CREATE_FULL:
                mthd = 'docs_create_single_card'
            getattr(AlephTransportExportService(export_instance), mthd)()
