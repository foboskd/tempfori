import logging
from typing import Optional, List
from pathlib import Path

from django.db import transaction

from d11 import models as d11_models
from d11.tasks import d11_mviews_rebuild
from project.contrib.db import get_sql_from_queryset

logger = logging.getLogger(__name__)

__all__ = [
    'AlephExportDocsServiceException',
    'AlephExportDocsServiceResultFileProcessException',
    'AlephExportDocsService',
]


########################################################################################################################
# BASE
########################################################################################################################

class AlephExportDocsServiceException(Exception):
    ...


class AlephExportDocsServiceResultFileProcessException(AlephExportDocsServiceException):
    ...


class AlephExportDocsService:
    export_instance: d11_models.ExportToAleph

    EXPORT_KIND: d11_models.ExportAlephKind

    ALEPH_SEQ_STRATEGY: str = 'full'

    def __init__(self, export_instance: d11_models.ExportToAleph):
        self.export_instance = export_instance

    @classmethod
    def make_import_instance_and_do_export(
            cls,
            docs_count: Optional[int] = None,
            is_updated_after_last_export: bool = False,
    ) -> d11_models.ExportToAleph:
        export_service = cls(cls.make_export_instance(
            docs_count=docs_count,
            is_updated_after_last_export=is_updated_after_last_export
        ))
        export_service.do_export()
        return export_service.export_instance

    def do_export(self, docs_count: Optional[int] = None) -> None:
        ...

    @classmethod
    def get_by_export_instance(cls, instance: d11_models.ExportToAleph):
        from d11.services.aleph_export import create
        from d11.services.aleph_export import update
        cl = {
            d11_models.ExportAlephKind.CREATE_FULL: create.AlephExportDocsCreateFullService,
            d11_models.ExportAlephKind.CREATE_SYNOPSIS: create.AlephExportDocsCreateSynopsisService,
            d11_models.ExportAlephKind.CREATE_DISSERTATION: create.AlephExportDocsCreateDissertationService,
            d11_models.ExportAlephKind.UPDATE_FULL: update.AlephExportDocsUpdateFullService,
            d11_models.ExportAlephKind.UPDATE_SYNOPSIS: update.AlephExportDocsUpdateSynopsisService,
            d11_models.ExportAlephKind.UPDATE_DISSERTATION: update.AlephExportDocsUpdateDissertationService,
        }.get(instance.kind)
        if not cl:
            raise AlephExportDocsServiceException("Can't get export instance by kind")
        return cl(instance)

    @classmethod
    def make_export_instance(
            cls,
            docs_count: Optional[int] = None,
            is_updated_after_last_export: bool = False
    ) -> d11_models.ExportToAleph:
        d11_mviews_rebuild()
        queryset = cls._get_export_docs_queryset()
        if is_updated_after_last_export:
            queryset = queryset.filter(exports_to_aleph__isnull=True)
        if docs_count:
            queryset = queryset[:docs_count]
        return cls._make_export_instance(queryset)

    @classmethod
    def make_export_instance_by_docs(cls, docs_ids: List[int]) -> d11_models.ExportToAleph:
        queryset = cls._get_export_docs_queryset().filter(id__in=docs_ids)
        return cls._make_export_instance(queryset)

    @classmethod
    @transaction.atomic
    def _make_export_instance(cls, queryset: d11_models.Doc.QuerySet) -> d11_models.ExportToAleph:
        instance = d11_models.ExportToAleph(kind=cls.EXPORT_KIND)
        instance.save()
        instance.docs_serialized_file.name = (
            d11_models.ExportToAleph._meta.get_field('docs_serialized_file').generate_filename(instance, '1.seq')
        )
        docs_serialized_file_path = Path(instance.docs_serialized_file.path)
        docs_serialized_file_path.parent.mkdir(parents=True, exist_ok=True)
        with docs_serialized_file_path.open('w') as f:
            for i, doc in enumerate(queryset):
                f.write(cls._get_doc_aleph_sec(doc, i))
        instance.save()
        instance.docs.add(*queryset.values_list('id', flat=True))
        return instance

    @classmethod
    def _get_export_docs_queryset(cls) -> d11_models.Doc.QuerySet:
        return cls._get_export_docs_queryset_base()

    @classmethod
    def _get_export_docs_queryset_base(cls) -> d11_models.Doc.QuerySet:
        return d11_models.Doc.objects \
            .filter(is_checked=True) \
            .distinct() \
            .prefetch_related(*d11_models.Doc.objects.get_queryset_prefetch_related())

    @classmethod
    def _get_doc_aleph_sec(cls, doc: d11_models.Doc, i: int) -> str:
        if cls.ALEPH_SEQ_STRATEGY == 'synopsis':
            return cls._get_doc_aleph_seq_synopsis(doc, i)
        if cls.ALEPH_SEQ_STRATEGY == 'dissertation':
            return cls._get_doc_aleph_seq_dissertation(doc, i)
        return cls._get_doc_aleph_seq_full(doc, i)

    @classmethod
    def _get_doc_aleph_seq_full(cls, doc: d11_models.Doc, i: int) -> str:
        return (
                ('\n' if i else '')
                + str(doc.get_serializer_aleph(doc_row_index=i * 2 + 1).synopsis)
                + '\n'
                + str(doc.get_serializer_aleph(doc_row_index=i * 2 + 2).dissertation)
        )

    @classmethod
    def _get_doc_aleph_seq_synopsis(cls, doc: d11_models.Doc, i: int) -> str:
        return (
                ('\n' if i else '')
                + str(doc.get_serializer_aleph(doc_row_index=i + 1).synopsis)
        )

    @classmethod
    def _get_doc_aleph_seq_dissertation(cls, doc: d11_models.Doc, i: int) -> str:
        return (
                ('\n' if i else '')
                + str(doc.get_serializer_aleph(doc_row_index=i + 1).dissertation)
        )
