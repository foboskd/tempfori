import datetime
import logging
from collections import namedtuple
from typing import Optional, List
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from d11 import models as d11_models
from d11.services.aleph_transport import AlephTransportExportService
from d11.services.aleph_import import AlephImportDocsService
from d11.services.aleph_export.base import AlephExportDocsService, AlephExportDocsServiceResultFileProcessException
from d11.services.aleph_export.update import AlephExportDocsUpdateFullService, AlephExportDocsUpdateSynopsisService, \
    AlephExportDocsUpdateDissertationService

__all__ = [
    'AlephExportDocsCreateFullService',
    'AlephExportDocsCreateSynopsisService',
    'AlephExportDocsCreateDissertationService',
]

from d11.tasks import d11_mviews_rebuild

logger = logging.getLogger(__name__)


class AlephExportDocsCreateFullService(AlephExportDocsService):
    EXPORT_KIND = d11_models.ExportAlephKind.CREATE_FULL
    TRANSPORT_METHOD = 'double'
    UPDATE_SERVICE_CLASS = AlephExportDocsUpdateFullService

    @transaction.atomic
    def do_export(self, docs_count: Optional[int] = None) -> None:
        if self.TRANSPORT_METHOD == 'single':
            AlephTransportExportService(self.export_instance).docs_create_single_card()
        else:
            AlephTransportExportService(self.export_instance).docs_create_both_cards()
        self.result_file_process()
        self.result_file_process_post_processing()

    @transaction.atomic
    def result_file_process(self) -> int:
        Row = namedtuple('Row', ['aleph_id', 'doc_id', 'kind'])
        rows: List[Row] = []
        with Path(self.export_instance.result_file.path).open() as f:
            for line in f:
                rows.append(Row(*list(map(lambda x: x.strip(), line.strip().split(',')))))
        docs_queryset = self._get_export_docs_queryset_base().filter(id__in=set(row.doc_id for row in rows))
        docs = {
            doc.id: doc
            for doc in docs_queryset
        }
        docs_cards_exist = [
            f'{card.doc_id}-{card.kind}'
            for card in d11_models.DocAlephCard.objects.filter(doc__in=docs.keys())
        ]
        if len(docs) < len(rows) / 2:
            error_msg = 'Docs count least than rows count/2'
            logger.error(error_msg, extra={'instance': self.export_instance})
            raise AlephExportDocsServiceResultFileProcessException(error_msg)
        docs_aleph_cards_for_create = []
        docs_for_update_last_date = set()
        for row in rows:
            doc = docs[int(row.doc_id)]
            kind = d11_models.DocAlephCardKind.DISSERTATION
            if row.kind == 'autoref':
                kind = d11_models.DocAlephCardKind.SYNOPSIS
            if f'{doc.id}-{kind}' in docs_cards_exist:
                continue
            docs_for_update_last_date.add(doc)
            docs_aleph_cards_for_create.append(
                d11_models.DocAlephCard(
                    doc=doc,
                    aleph_id=row.aleph_id,
                    kind=kind
                )
            )
        if not docs_aleph_cards_for_create:
            return 0
        docs_aleph_cards = d11_models.DocAlephCard.objects.bulk_create(docs_aleph_cards_for_create)
        for doc_for_update in docs_for_update_last_date:
            doc_for_update.last_date_abis_manual_changes = timezone.now()
            doc_for_update.save()
        for card in docs_aleph_cards:
            card.file_set()
        d11_mviews_rebuild()
        return len(docs_aleph_cards)

    @transaction.atomic
    def result_file_process_post_processing(self):
        docs_created_ids = self.export_instance.docs.values_list('id', flat=True)
        import_service = AlephImportDocsService(
            AlephImportDocsService.make_import_instance_by_docs_ids(docs_created_ids)
        )
        import_service.do_import()
        d11_mviews_rebuild()
        update_service = self.UPDATE_SERVICE_CLASS(
            self.UPDATE_SERVICE_CLASS.make_export_instance_by_docs(docs_created_ids)
        )
        update_service.do_export()

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return super()._get_export_docs_queryset_base().filter(
            is_sync_synopsis_to_abis=True,
            advanced_attributes__aleph_card_synopsis_id__isnull=True,
            is_sync_dissertation_to_abis=True,
            advanced_attributes__aleph_card_dissertation_id__isnull=True,
            advanced_attributes__defense_date__lte=datetime.datetime.now() + datetime.timedelta(days=1),
        )


class AlephExportDocsCreateSynopsisService(AlephExportDocsCreateFullService):
    EXPORT_KIND = d11_models.ExportAlephKind.CREATE_SYNOPSIS
    TRANSPORT_METHOD = 'single'
    UPDATE_SERVICE_CLASS = AlephExportDocsUpdateSynopsisService
    ALEPH_SEQ_STRATEGY = 'synopsis'

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return super()._get_export_docs_queryset_base().filter(
            is_sync_synopsis_to_abis=True,
            advanced_attributes__aleph_card_synopsis_id__isnull=True,
        )


class AlephExportDocsCreateDissertationService(AlephExportDocsCreateFullService):
    EXPORT_KIND = d11_models.ExportAlephKind.CREATE_DISSERTATION
    TRANSPORT_METHOD = 'single'
    UPDATE_SERVICE_CLASS = AlephExportDocsUpdateDissertationService
    ALEPH_SEQ_STRATEGY = 'dissertation'

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return super()._get_export_docs_queryset_base().filter(
            is_sync_dissertation_to_abis=True,
            advanced_attributes__aleph_card_dissertation_id__isnull=True,
            advanced_attributes__defense_date__lte=datetime.datetime.now()  # + datetime.timedelta(days=1),
        )
