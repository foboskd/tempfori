import datetime

from dateutil.parser import parse as date_parse
from django.core.management.base import BaseCommand

from d11.models import Source
from d11.tasks import d11_call_collector_method


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('date_from', nargs='?')
        parser.add_argument('date_to', nargs='?')
        parser.add_argument('-s', '--source', nargs='*')
        parser.add_argument('-a', '--async', dest='is_async', action='store_true')

    def handle(self, *args, **options):
        date_from = None
        date_to = None
        if options['date_from']:
            date_from = date_parse(options['date_from']).date()
            date_to = date_from + datetime.timedelta(days=1)
        if options['date_to']:
            date_to = date_parse(options['date_to']).date()
        source_qs = Source.objects.all()
        if options['source']:
            source_qs = source_qs.filter(id__in=options['source'])
        for source in source_qs:
            collector = source.get_collector(date_from=date_from, date_to=date_to, is_async=options['is_async'])
            if options['is_async']:
                d11_call_collector_method.delay(collector, 'start')
            else:
                collector.start()
