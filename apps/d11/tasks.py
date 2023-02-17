import datetime
from typing import Optional

from django.core.management import call_command
from django.conf import settings

from project.celery import app
from d11.collector import CollectorAbstract


@app.task()
def d11_collect_vak_all():
    from d11.models import Source
    call_command(
        'collect_vak',
        date_to=str(datetime.datetime.now().date() + datetime.timedelta(days=settings.EXTERNAL_SOURCE_VAK_DAYS_DEPTH)),
        source=Source.objects.filter(is_enabled=True).values_list('id', flat=True),
        is_async=True,
    )


@app.task()
def d11_call_collector_method(collector: CollectorAbstract, method: str, *args, **kwargs):
    return getattr(collector, method)(*args, **kwargs)


@app.task()
def d11_export_to_aleph_new_docs_full(docs_count: Optional[int] = None):
    from d11.services.aleph_export import AlephExportDocsCreateFullService
    AlephExportDocsCreateFullService.make_import_instance_and_do_export(docs_count=docs_count)


@app.task()
def d11_export_to_aleph_new_docs_synopsis(docs_count: Optional[int] = None):
    from d11.services import aleph_export
    aleph_export.AlephExportDocsCreateSynopsisService.make_import_instance_and_do_export(docs_count=docs_count)


@app.task()
def d11_export_to_aleph_new_docs_dissertation(docs_count: Optional[int] = None):
    from d11.services import aleph_export
    aleph_export.AlephExportDocsCreateDissertationService.make_import_instance_and_do_export(docs_count=docs_count)


@app.task()
def d11_export_to_aleph_exist(docs_count: Optional[int] = None, is_updated_after_last_export: bool = False):
    from d11.services.aleph_export import AlephExportDocsUpdateFullService
    AlephExportDocsUpdateFullService.make_import_instance_and_do_export(
        docs_count=docs_count,
        is_updated_after_last_export=is_updated_after_last_export
    )


@app.task()
def d11_import_from_aleph():
    from d11.services.aleph_import import AlephImportDocsService
    AlephImportDocsService.make_import_instance_and_do_import()


@app.task()
def d11_export_aleph_cards_files(is_all: bool = False):
    from d11.services.aleph_cards_files_external_storage import AlephCardsFilesExternalStorageService
    AlephCardsFilesExternalStorageService.make_import_instance_and_do_export(is_all=is_all)


@app.task()
def d11_mviews_rebuild():
    from d11 import models as d11_models
    d11_models.DocAdvancedAttributes.objects.rebuild()
    d11_models.DocFullNameDoubles.objects.rebuild()
