import logging
from typing import Optional

from django.db import transaction

from d11 import models as d11_models
from d11.services.aleph_import import AlephImportDocsService
from d11.services.aleph_transport import AlephTransportExportService
from d11.services.aleph_export.base import AlephExportDocsService

__all__ = [
    'AlephExportDocsUpdateFullService',
    'AlephExportDocsUpdateSynopsisService',
    'AlephExportDocsUpdateDissertationService',
]

from d11.tasks import d11_mviews_rebuild

logger = logging.getLogger(__name__)


class AlephExportDocsUpdateFullService(AlephExportDocsService):
    EXPORT_KIND = d11_models.ExportAlephKind.UPDATE_FULL

    def do_export(self, docs_count: Optional[int] = None):
        AlephTransportExportService(self.export_instance).docs_update()
        d11_mviews_rebuild()
        self.export_post_processing()

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return super()._get_export_docs_queryset_base().filter(
            advanced_attributes__aleph_card_synopsis_id__isnull=False,
            advanced_attributes__aleph_card_dissertation_id__isnull=False,
        )

    @transaction.atomic
    def export_post_processing(self):
        docs_updated_ids = self.export_instance.docs.values_list('id', flat=True)
        import_service = AlephImportDocsService(
            AlephImportDocsService.make_import_instance_by_docs_ids(docs_updated_ids)
        )
        import_service.do_import()
        d11_mviews_rebuild()


class AlephExportDocsUpdateSynopsisService(AlephExportDocsUpdateFullService):
    EXPORT_KIND = d11_models.ExportAlephKind.UPDATE_SYNOPSIS
    ALEPH_SEQ_STRATEGY = 'synopsis'

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return super()._get_export_docs_queryset_base().filter(
            is_sync_synopsis_to_abis=True,
            advanced_attributes__aleph_card_synopsis_id__isnull=False,
        )


class AlephExportDocsUpdateDissertationService(AlephExportDocsUpdateFullService):
    EXPORT_KIND = d11_models.ExportAlephKind.UPDATE_DISSERTATION
    ALEPH_SEQ_STRATEGY = 'dissertation'

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return super()._get_export_docs_queryset_base().filter(
            is_sync_dissertation_to_abis=True,
            advanced_attributes__aleph_card_dissertation_id__isnull=False,
        )
