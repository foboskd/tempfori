from __future__ import absolute_import, unicode_literals
from django.db.models.signals import post_migrate, pre_migrate
from project.contrib.db.signals_receivers import pre_migrate_app, post_migrate_app
from project.celery import app as celery_app

pre_migrate.connect(pre_migrate_app, weak=False)
post_migrate.connect(post_migrate_app, weak=False)
