from django.core.management.base import BaseCommand

from d11.services.aleph_import import AlephImportDocsService


class Command(BaseCommand):
    def handle(self, *args, **options):
        return str(AlephImportDocsService.make_import_instance().id)
