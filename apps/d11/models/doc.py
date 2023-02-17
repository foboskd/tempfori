import logging
import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union, Any, Dict, List
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

from project.contrib.datetime import date_parse
from project.contrib.db.models import DatesModelBase, ModelDiffMixin, MaterializedViewModel

if TYPE_CHECKING:
    from d11.models.doc_aleph import DocAlephCard
    from d11.serializers.aleph import DocAlephSerializerAbstract

__all__ = [
    'DocFieldType',
    'DocField',
    'Doc',
    'DocFieldValue',
    'DocFileValue',
    'DocAdvancedAttributes',
    'DocFullNameDoubles',
]


def doc_upload_to(instance: 'Doc', filename: str) -> str:
    return str(
        instance.EXTERNAL_SOURCE_UPLOAD_TO
        / instance.id_verbose[:3]
        / instance.id_verbose[3:6]
        / f'{instance.id_verbose}{Path(filename).suffix}'
    )


def doc_file_value_upload_to(instance: 'DocFileValue', filename: str) -> str:
    return str(
        instance.UPLOAD_TO
        / instance.doc.id_verbose[:3]
        / instance.doc.id_verbose[3:6]
        / f'{instance.doc.id_verbose}-{instance.field.name}{Path(filename).suffix}'
    )


class DocFieldType(models.TextChoices):
    STR = 'str', 'Строка'
    INT = 'int', 'Целое число'
    FLOAT = 'float', 'Число'
    DATE = 'date', 'Дата'
    DATETIME = 'datetime', 'Дата и время'
    FILE = 'file', 'Файл'

    def python_value(self, value: Any) -> Union[str, int, float, datetime.date, datetime.datetime]:
        cast_type, cast_fnc = {
            self.STR: (str, str),
            self.INT: (int, int),
            self.FLOAT: (float, float),
            self.DATE: (datetime.date, lambda x: date_parse(x).date()),
            self.DATETIME: (datetime.datetime, date_parse),
            self.FILE: (Path, lambda x: Path(settings.MEDIA_ROOT) / DocField.FILES_DIRNAME_IN_MEDIA_ROOT / Path(x)),
        }[self]
        if not isinstance(value, cast_type):
            value = cast_fnc(value)
        return value

    @classmethod
    def get_objects(cls) -> Dict[str, 'DocFieldType']:
        return {c.value: c for c in cls}


class DocField(models.Model):
    FILES_DIRNAME_IN_MEDIA_ROOT = 'files-raw'

    name = models.CharField(max_length=1000, null=True, blank=True, unique=True, verbose_name=_('название'))
    label = models.CharField(max_length=1000, unique=True, verbose_name=_('заголовок'))
    label_aliases = ArrayField(models.CharField(max_length=1000), null=True, blank=True, verbose_name=_('синонимы'))
    type = models.CharField(
        max_length=50, choices=DocFieldType.choices, default=DocFieldType.STR,
        verbose_name=_('тип')
    )
    is_auto = models.BooleanField(default=True, verbose_name=_('создано автоматически'))
    sorting = models.IntegerField(default=0, verbose_name=_('сортировка'))

    class Meta:
        verbose_name = _('поле записей')
        verbose_name_plural = _('поля записей')
        ordering = ['sorting', 'name', 'label']

    class QuerySet(models.QuerySet):
        pass

    class Manager(models.Manager.from_queryset(QuerySet)):
        def get_by_label(self, label: str) -> Optional['DocField']:
            return self.get_queryset().filter(
                models.Q(label=label)
                | models.Q(label_aliases__contains=[label])
            ).first()

        def get_by_name(self, name: str) -> Optional['DocField']:
            return self.get_queryset().filter(name=name).first()

    objects = Manager()

    def __str__(self):
        return self.label


class Doc(ModelDiffMixin, DatesModelBase):
    EXTERNAL_SOURCE_UPLOAD_TO = Path('docs-sources')

    source = models.ForeignKey('d11.Source', on_delete=models.RESTRICT, verbose_name=_('источник'))
    url = models.URLField(max_length=1000, unique=True, verbose_name=_('URL'))
    content_file = models.FileField(
        upload_to=doc_upload_to, null=True, blank=True,
        verbose_name=_('файл карточки на сайте источнике')
    )
    content_file_hash = models.CharField(
        max_length=32, null=True, blank=True,
        verbose_name=_('md5 файла карточки на сайте источнике')
    )

    last_date_abis_manual_changes = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_('дата последнего сделанного в Алеф изменения'),
        help_text=_('Справочное поле, заполняется при экспорте автореферата или диссертации в Алеф, '
                    'а после этого вручную'),
    )

    is_checked = models.BooleanField(default=False, verbose_name=_('проверено'))
    # is_synopsis_exists = models.BooleanField(default=False, verbose_name=_('наличие автореферата'))
    is_sync_synopsis_to_abis = models.BooleanField(default=False, verbose_name=_('загрузить автореферат в Алеф'))
    is_sync_dissertation_to_abis = models.BooleanField(
        default=False,
        verbose_name=_('загрузить диссертацию в Алеф'),
        help_text=_('по достижению даты защиты')
    )
    is_track_external = models.BooleanField(default=True, verbose_name=_('отслеживать ВАК'))

    class Meta:
        ordering = ['created_at']
        verbose_name = _('запись')
        verbose_name_plural = _('записи')

    class QuerySet(models.QuerySet):
        pass

    class Manager(models.Manager.from_queryset(QuerySet)):
        @classmethod
        def get_queryset_prefetch_related(cls) -> List[str]:
            return [
                'source',
                'fields_values', 'fields_values__field',
                'files_values', 'files_values__field',
                'aleph_cards', 'advanced_attributes',
            ]

    objects = Manager()

    def __str__(self):
        return f'{self.id} :: {self.source_id}'

    def get_value_by_name(self, value_name: str):
        return {
            value.field.name: value.python_value
            for value in self.fields_values.all()
        }.get(value_name)

    def get_file_value_by_name(self, value_name: str):
        return {
            value.field.name: value
            for value in self.files_values.all()
        }.get(value_name)

    def get_cards_dict(self) -> Dict[str, 'DocAlephCard']:
        return {
            card.kind: card
            for card in self.aleph_cards.all()
        }

    def get_serializer_aleph(self, **kwargs) -> 'DocAlephSerializerAbstract':
        return self.source.get_collector_class().doc_serializer_aleph_class(self, **kwargs)

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(9)

    @property
    def full_name(self) -> Optional[str]:
        return self.get_value_by_name('full_name')

    @property
    def defense_date(self) -> Optional[datetime.date]:
        return self.get_value_by_name('defense_date')

    @property
    def fields_updated_at(self) -> Optional[datetime.datetime]:
        return max(f.updated_at for f in self.fields_values.all())

    @property
    def updated_at_last(self) -> datetime.datetime:
        updated_at_fields = self.fields_updated_at
        if updated_at_fields:
            return max(self.updated_at, updated_at_fields)
        return self.updated_at


class DocFieldValue(DatesModelBase):
    doc = models.ForeignKey(
        'd11.Doc', on_delete=models.CASCADE, related_name='fields_values',
        verbose_name=_('запись')
    )
    field = models.ForeignKey(
        'd11.DocField', on_delete=models.CASCADE, related_name='docs_values',
        limit_choices_to=~models.Q(type=DocFieldType.FILE),
        verbose_name=_('поле')
    )
    value = models.JSONField(verbose_name=_('значение'))

    class Meta:
        ordering = [f'field__{f}' for f in DocField._meta.ordering]
        unique_together = [
            ['doc', 'field']
        ]
        verbose_name = _('значение поля записи')
        verbose_name_plural = _('значения полей записи')

    def __str__(self):
        return f'{self.id} :: {self.doc_id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.post_save_juggling()

    @property
    def python_value(self):
        return DocFieldType.get_objects()[self.field.type].python_value(self.value)

    def post_save_juggling(self):
        if self.field.name:
            if juggling_method := getattr(self, f'_juggling_{self.field.name}', None):
                try:
                    juggling_method()
                except Exception as e:
                    logging.error('post_save_juggling ERROR', extra={
                        'doc_id': self.doc_id,
                        'field_id': self.field_id,
                        'value': self.value,
                        'error': e.args
                    })


class DocFileValue(DatesModelBase):
    UPLOAD_TO = Path('docs-files')

    doc = models.ForeignKey(
        'd11.Doc', on_delete=models.CASCADE, related_name='files_values',
        verbose_name=_('запись')
    )
    field = models.ForeignKey(
        'd11.DocField', on_delete=models.CASCADE, related_name='docs_files',
        limit_choices_to=models.Q(type=DocFieldType.FILE),
        verbose_name=_('поле')
    )
    value = models.FileField(
        upload_to=doc_file_value_upload_to,
        verbose_name=_('файл'),
        help_text=_('актуально только для в случае, если не создана соответствующая карточка Алеф')
    )

    class Meta:
        ordering = [f'field__{f}' for f in DocField._meta.ordering]
        unique_together = [
            ['doc', 'field']
        ]
        verbose_name = _('файл записи')
        verbose_name_plural = _('файлы записи')

    def __str__(self):
        return f'{self.id} :: {self.doc_id}'

    @property
    def python_value(self):
        return self.value


class DocAdvancedAttributes(MaterializedViewModel):
    doc = models.OneToOneField(
        'd11.Doc', primary_key=True, on_delete=models.DO_NOTHING,
        related_name='advanced_attributes',
    )

    full_name = models.CharField(max_length=500, null=True, blank=True)
    defense_date = models.DateField(null=True, blank=True)
    is_has_updates_after_abis_manual_changes = models.BooleanField(
        default=False,
        verbose_name=_('Запись обновлена после внесения изменения в Алеф')
    )

    values_created_at_max = models.DateTimeField(null=True, blank=True)
    values_created_at_min = models.DateTimeField(null=True, blank=True)
    values_updated_at_max = models.DateTimeField(null=True, blank=True)
    values_updated_at_min = models.DateTimeField(null=True, blank=True)

    aleph_card_synopsis = models.ForeignKey(
        'd11.DocAlephCard', null=True, blank=True,
        related_name='doc_advanced_attributes_synopsis', on_delete=models.DO_NOTHING,
    )
    aleph_card_synopsis_aleph_id = models.CharField(max_length=20, null=True, blank=True)
    aleph_card_synopsis_aleph_created_at = models.DateTimeField(null=True, blank=True)
    aleph_card_synopsis_aleph_updated_at = models.DateTimeField(null=True, blank=True)

    aleph_card_dissertation = models.ForeignKey(
        'd11.DocAlephCard', null=True, blank=True,
        related_name='doc_advanced_attributes_dissertation', on_delete=models.DO_NOTHING,
    )
    aleph_card_dissertation_aleph_id = models.CharField(max_length=20, null=True, blank=True)
    aleph_card_dissertation_created_at = models.DateTimeField(null=True, blank=True)
    aleph_card_dissertation_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'vm_d11_doc_advanced_attributes'


class DocFullNameDoubles(MaterializedViewModel):
    doc = models.OneToOneField(
        'd11.Doc', primary_key=True, on_delete=models.DO_NOTHING,
        related_name='full_name_doubles',
    )

    full_name = models.CharField(max_length=500)
    docs_count = models.IntegerField()
    docs_ids = ArrayField(models.BigIntegerField())

    class Meta:
        managed = False
        db_table = 'vm_d11_doc_full_name_doubles'
