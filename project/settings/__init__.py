import sys
from pathlib import Path
from os import environ
from split_settings.tools import include, optional

sys.path.append('apps')

DEBUG = False

BASE_URL = 'http://dissertation-db.neb.rsl'
BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.setdefault('DJANGO_ENV', 'dev')
DJANGO_ENV = environ['DJANGO_ENV']

SECRET_KEY = 'django-insecure-qasdasdjk123-2mw(kwl1g&-t28nvir)jby8mk%%64ad$@v4_mnkgz&m=$-92kn'

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['*']

_base_settings = (
    'bits/aleph.py',
    'bits/db.py',
    'bits/acc.py',
    'bits/locale.py',
    'bits/static.py',
    'bits/redis.py',
    'bits/cache.py',
    'bits/celery.py',
    'bits/email.py',
    'bits/log.py',
    'bits/external_file_storage.py',
    'bits/external_sources.py',
    'bits/api.py',
    f'envs/{DJANGO_ENV}.py',
    optional('settings_local.py'),
    'bits/_last.py',
)

include(*_base_settings)
