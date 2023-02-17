import os

import dj_database_url

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASE_ENGINE_POSTGRESQL = 'django.db.backends.postgresql'

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'd11-pg')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'd11')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'not1pass')

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://{user}:{password}@{host}/{db}'.format(
            user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, db=POSTGRES_DB)
    ),
}

if 'OPTIONS' not in DATABASES['default']:
    DATABASES['default']['OPTIONS'] = {}
DATABASES['default']['OPTIONS']['CONN_MAX_AGE'] = None
