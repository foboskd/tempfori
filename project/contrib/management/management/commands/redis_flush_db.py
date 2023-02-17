import redis
from django.core.management.base import BaseCommand
from django.conf import settings

from . import logger


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('db', type=int, nargs='*')

    def handle(self, *args, **options):
        if not settings.REDIS_ENABLED:
            return 'REDIS DISABLED'
        for db in options.get('db'):
            result = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=db).flushdb()
            if options['verbosity']:
                logger.info('%s\t%s' % (db, result))
