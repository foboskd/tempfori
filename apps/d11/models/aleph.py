from pathlib import Path

from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase
from main.services.mark import AlephSequentialReader

__all__ = [
    'ExportAlephKind',
    'ExportToAleph',
    'ImportFromAleph',
]


def import_export_upload_to(instance: 'ImportExportAlephAbstract', filename: str, name: str) -> str:
    return str(
        instance.UPLOAD_TO
        / instance.id_verbose[:3]
        / instance.id_verbose[3:6]
        / f'{instance.id_verbose}-{name}{Path(filename).suffix}'
    )


def import_export_upload_to_serialized_file(instance: 'ImportExportAlephAbstract', filename: str) -> str:
    return import_export_upload_to(instance, filename, 'docs')


def import_export_upload_to_result_file(instance: 'ImportExportAlephAbstract', filename: str) -> str:
    return import_export_upload_to(instance, filename, 'result')


class ExportAlephKind(models.TextChoices):
    CREATE_FULL = 'create_full', _('Создание обеих карточек')
    CREATE_SYNOPSIS = 'create_synopsis', _('Создание авторефератов')
    CREATE_DISSERTATION = 'create_dissertation', _('Создание диссертаций')
    UPDATE_FULL = 'update_full', _('Обновление обеих карточек')
    UPDATE_SYNOPSIS = 'update_synopsis', _('Обновление авторефератов')
    UPDATE_DISSERTATION = 'update_dissertation', _('Обновление диссертаций')


class ImportExportAlephAbstract(DatesModelBase):
    UPLOAD_TO = Path('aleph')

    docs_serialized_file = models.FileField(
        null=True, blank=True, upload_to=import_export_upload_to_serialized_file,
        verbose_name=_('файл c записями для загрузки в Aleph'),
        help_text=_('формат Aleph SEQ')
    )
    result_file = models.FileField(
        null=True, blank=True, upload_to=import_export_upload_to_result_file,
        verbose_name=_('файл c результатами из Aleph'),
        help_text=_('формат Aleph SEQ')
    )
    extra = models.JSONField(default=dict, help_text=_('доп. данные'))

    class Meta:
        abstract = True
        ordering = ['-created_at']

    @property
    def docs_count(self) -> int:
        return len(self.docs.all())

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(9)


class ExportToAleph(ImportExportAlephAbstract):
    UPLOAD_TO = ImportExportAlephAbstract.UPLOAD_TO / 'export'

    docs = models.ManyToManyField('d11.Doc', related_name='exports_to_aleph', verbose_name=_('записи'))
    kind = models.CharField(max_length=50, choices=ExportAlephKind.choices, verbose_name=_('тип'))

    class Meta:
        verbose_name = _('экспорт записей в Алеф')
        verbose_name_plural = _('экспорты записей в Алеф')


class ImportFromAleph(ImportExportAlephAbstract):
    UPLOAD_TO = ImportExportAlephAbstract.UPLOAD_TO / 'import'

    docs = models.ManyToManyField('d11.Doc', related_name='imports_from_aleph', verbose_name=_('записи'))

    class Meta:
        verbose_name = _('импорт записей из Алеф')
        verbose_name_plural = _('импорты записей из Алеф')

    def result_record_iter(self) -> AlephSequentialReader:
        with Path(self.result_file.path).open('r') as f:
            reader = AlephSequentialReader(f)
            for record in reader:
                yield record
