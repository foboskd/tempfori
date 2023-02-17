from django.core.management.base import BaseCommand

from d11.tasks import d11_mviews_rebuild


class Command(BaseCommand):
    def handle(self, *args, **options):
        d11_mviews_rebuild()
