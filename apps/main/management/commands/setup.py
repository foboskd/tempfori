from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('create_admin')
        call_command('setup_sources')
        call_command('setup_doc_fields', force=True)
        call_command('setup_ref')
        call_command('setup_celery_schedule')
