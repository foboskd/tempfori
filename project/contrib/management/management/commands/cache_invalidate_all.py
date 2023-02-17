from redis import StrictRedis
from cacheops import invalidate_all
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import caches

from . import logger


class Command(BaseCommand):
    def handle(self, *args, **options):
        exclude = []
        if settings.REDIS_ENABLED:
            redis_dbs = [
                settings.CACHEOPS_REDIS['db'],
            ]
            for cache in settings.CACHES.values():
                if 'redis' in cache['BACKEND']:
                    redis_dbs.append(cache['OPTIONS']['DB'])
            for db in sorted(redis_dbs):
                if db in exclude:
                    continue
                redis = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=db)
                logger.info('%s\t%s' % (db, redis.flushdb()))
        else:
            invalidate_all()
            for k in settings.CACHES:
                caches[k].clear()
                logger.info('%s\tTrue' % k)
