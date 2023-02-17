import redis
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('console_no_level')


class Command(BaseCommand):
    def handle(self, *args, **options):
        redis.Redis.from_url(settings.SESSION_REDIS_URL).flushall()
