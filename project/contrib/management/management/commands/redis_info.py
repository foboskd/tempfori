import redis
import subprocess
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('console_no_level')


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.REDIS_ENABLED:
            return 'REDIS DISABLED'
        s = ''
        for k, v in sorted(
                redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT).info().items(),
                key=lambda x: x[0] if not x[0].startswith('db') else 'z%s' % x[0]
        ):
            s += '%s %s\n' % (
                k, v if not isinstance(v, dict) else ','.join(['%s=%s' % (vk, vv) for vk, vv in v.items()]))
        subprocess.call('echo "%s" | column -t -s\' \'' % s, shell=True)
