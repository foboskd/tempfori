#!/bin/sh

set -e

/app/docker/entry-point/${DJANGO_ENV:-prod}/$1.sh