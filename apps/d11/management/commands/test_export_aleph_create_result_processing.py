from django.core.management.base import BaseCommand

from d11.models.aleph import ExportToAleph
from d11.services.aleph_export import AlephExportDocsService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('exports_ids', type=int, nargs='*')

    def handle(self, *args, **options):
        for export_instance in ExportToAleph.objects.filter(id__in=options['exports_ids']):
            AlephExportDocsService.get_by_export_instance(export_instance).result_file_process()
