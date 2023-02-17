#!/bin/sh

set -e

celery --app=project beat --loglevel=info --pidfile=