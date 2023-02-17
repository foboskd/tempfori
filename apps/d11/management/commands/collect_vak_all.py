from django.core.management.base import BaseCommand

from d11.tasks import d11_collect_vak_all


class Command(BaseCommand):
    def handle(self, *args, **options):
        d11_collect_vak_all.delay()
