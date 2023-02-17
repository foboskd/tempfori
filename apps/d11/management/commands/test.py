from django.core.management.base import BaseCommand

from d11.models import Source
from d11.tasks import d11_mviews_rebuild


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.test_do_item()
        d11_mviews_rebuild()

    def test_do_item(self, *args, **options):
        advert = Source.objects.get(id=1)
        indi = Source.objects.get(id=2)
        test_ids = [
            [advert, '100064609'],
            # [indi, '91649272002'],
        ]
        for source, item_id in test_ids:
            collector = source.get_collector()
            item = collector.do_item(f'{collector.base_url}/{collector.item_url_prefix}/{item_id}', force=True)
            print(item)
