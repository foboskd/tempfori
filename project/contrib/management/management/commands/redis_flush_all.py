import redis
from django.core.management.base import BaseCommand
from django.conf import settings

from . import logger


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.REDIS_ENABLED:
            return 'REDIS DISABLED'
        redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT).flushall()
