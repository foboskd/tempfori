import django
from django.conf import settings
from django.core.management.commands.dumpdata import Command as CommandBase


class Command(CommandBase):
    def handle(self, *args, **options):
        settings.LOGGING['loggers']['']['level'] = 'ERROR'
        django.setup()
        super().handle(*args, **options)
