#!/bin/sh

set -e

celery --app=project worker --concurrency=8 --loglevel=info
