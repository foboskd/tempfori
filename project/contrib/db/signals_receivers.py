import os
from django.conf import settings
from django.db import connection

from . import load_sql_from_file, load_sql_from_python_module


def pre_migrate_app(**kwargs):
    load_app_sql(name='pre_migrate', **kwargs)


def post_migrate_app(**kwargs):
    load_app_sql(name='post_migrate', **kwargs)


def load_app_sql(name, **kwargs):
    app = kwargs['sender']
    app_dir = os.path.normpath(os.path.join(app.path, 'sql'))
    files = [
        os.path.join(app_dir, "%s.%s.sql" % (name, settings.DATABASES['default']['ENGINE'])),
        os.path.join(app_dir, "%s.sql" % name),
        os.path.join(app_dir, "%s.%s.py" % (name, settings.DATABASES['default']['ENGINE'])),
        os.path.join(app_dir, "%s.py" % name)

    ]
    for filepath in files:
        if os.path.exists(filepath):
            fnc = load_sql_from_file
            if os.path.splitext(filepath)[-1][1:] == 'py':
                fnc = load_sql_from_python_module
            fnc(filepath, connection=connection)
