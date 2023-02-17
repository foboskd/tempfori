import datetime
import logging
import json
from typing import List
from pathlib import Path

from django.db import transaction
from django.conf import settings

from d11 import models as d11_models
from d11.services.aleph_transport import AlephTransportImportService
from d11.tasks import d11_mviews_rebuild

logger = logging.getLogger(__name__)


class AlephImportDocsServiceException(Exception):
    ...


class AlephImportDocsService:
    import_instance: d11_models.ImportFromAleph

    def __init__(self, import_instance: d11_models.ImportFromAleph):
        self.import_instance = import_instance

    @classmethod
    def make_import_instance_and_do_import(cls) -> d11_models.ImportFromAleph:
        instance = cls(cls.make_import_instance())
        instance.do_import()
        return instance.import_instance

    def do_import(self):
        AlephTransportImportService(self.import_instance).docs_import()
        self.result_file_process()

    @classmethod
    def make_import_instance(cls) -> d11_models.ImportFromAleph:
        return cls._make_export_instance(cls._get_import_docs_queryset())

    @classmethod
    def make_import_instance_by_docs_ids(cls, docs_ids: List[int]) -> d11_models.ImportFromAleph:
        return cls._make_export_instance(cls._get_import_docs_queryset().filter(id__in=docs_ids))

    @classmethod
    @transaction.atomic
    def _make_export_instance(cls, queryset: d11_models.Doc.QuerySet) -> d11_models.ImportFromAleph:
        d11_mviews_rebuild()
        instance = d11_models.ImportFromAleph()
        instance.save()
        instance.docs_serialized_file.name = (
            d11_models.ImportFromAleph._meta.get_field('docs_serialized_file').generate_filename(
                instance, '1.aleph_id_list')
        )
        docs_serialized_file_path = Path(instance.docs_serialized_file.path)
        docs_serialized_file_path.parent.mkdir(parents=True, exist_ok=True)
        cards_ids = []
        for doc in queryset:
            cards_ids += [
                card.aleph_id
                for card in doc.aleph_cards.all()
            ]
        with docs_serialized_file_path.open('w') as f:
            f.write('\n'.join(map(cls.get_aleph_full_id, cards_ids)))
        instance.save()
        instance.docs.add(*queryset.values_list('id', flat=True))
        return instance

    @classmethod
    def _get_import_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return d11_models.Doc.objects.distinct().prefetch_related(
            *d11_models.Doc.objects.get_queryset_prefetch_related()
        ).filter(
            aleph_cards__isnull=False,
            # is_sync_abis=True,
        )

    @classmethod
    def get_aleph_full_id(cls, aleph_id: str) -> str:
        return f'{aleph_id}{settings.ALEPH_IMPORT_ALEPH_ID_SUFFIX}'

    @transaction.atomic
    def result_file_process(self) -> None:
        cards_records = {}
        docs_ids = set()
        stop_sync_docs_ids = set()
        for row in self.import_instance.result_record_iter():
            record_d11_data = row.as_d11_dict()
            doc_id = int(record_d11_data['911']['b'])
            cards_records[row.aleph_id] = record_d11_data
            # if row['911']['c'] == 'disser' and record_d11_data['500']['a'].lower() != 'предзащита':
            #     stop_sync_docs_ids.add(doc_id)
            docs_ids.add(doc_id)
        self.import_instance.extra = {
            'docs_ids': list(docs_ids),
            'stop_sync_docs_ids': list(stop_sync_docs_ids),
        }
        self.import_instance.save()
        if stop_sync_docs_ids:
            d11_models.Doc.objects \
                .filter(id__in=stop_sync_docs_ids) \
                .update(is_track_external=False, is_sync_synopsis_to_abis=False, is_sync_dissertation_to_abis=False)
        d11_cards = {
            card.aleph_id: card
            for card in d11_models.DocAlephCard.objects.filter(aleph_id__in=cards_records.keys())
        }
        for card_id, card_dict in cards_records.items():
            d11_card = d11_cards[card_id]
            d11_card.aleph_fields_json = card_dict
            ch_dates = d11_card.aleph_fields_json['CAT']
            if not isinstance(ch_dates, (list, tuple)):
                ch_dates = [ch_dates]
            ch_dates = sorted([
                datetime.datetime(
                    year=int(c['c'][:4]), month=int(c['c'][4:6]), day=int(c['c'][6:8]),
                    hour=int(c['h'][:2]), minute=int(c['h'][2:4]),
                )
                for c in ch_dates
            ])
            d11_card.save()
            if ch_dates:
                d11_card.doc.last_date_abis_manual_changes = ch_dates[-1]
                d11_card.doc.save()
