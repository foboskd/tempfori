from django.core.management.base import BaseCommand

from d11.services.aleph_export import AlephExportDocsUpdateFullService


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=None)

    def handle(self, *args, **options):
        return str(AlephExportDocsUpdateFullService.make_export_instance(docs_count=options['count']).id)
