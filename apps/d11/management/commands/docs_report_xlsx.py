from django.core.management.base import BaseCommand

from d11.models import Doc
from d11.services.report_xlsx import get_doc_fields_report_xlsx


class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = Doc.objects.filter(advanced_attributes__aleph_card_synopsis_id__isnull=False)
        # queryset = queryset.filter(id=4436)
        wb = get_doc_fields_report_xlsx(queryset)
        wb.save('1.xlsx')
