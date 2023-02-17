#!/bin/sh

set -e

/app/manage.py cache_invalidate_all
/app/manage.py migrate --fake-initial --noinput || exit 1
/app/manage.py setup

uwsgi --harakiri=60 --master --lazy-apps -p $UWSGI_WORKERS --max-requests 100000 --disable-logging --http 0.0.0.0:8000 -w project.wsgi
