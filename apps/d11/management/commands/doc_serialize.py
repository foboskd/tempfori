from django.core.management.base import BaseCommand

from d11.models import Doc


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('id', type=int, nargs='*')

    def handle(self, *args, **options):
        for doc_id in options['id']:
            print('*' * 120)
            doc_serializer = Doc.objects.get(id=doc_id).get_serializer_aleph()
            print(doc_serializer.synopsis)
            print()
            print(doc_serializer.dissertation)
