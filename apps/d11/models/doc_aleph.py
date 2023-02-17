import shutil
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase

__all__ = [
    'DocAlephCardKind',
    'DocAlephCard',
    'DocAlephCardFilesExport',
]


def doc_aleph_card_upload_to(instance: 'DocAlephCard', filename: str) -> str:
    aid = instance.aleph_id
    lib = 'rsl01'
    return str(
        instance.UPLOAD_TO
        / (lib + aid[:3] + '0' * 6 + '/' + lib + aid[:6] + '0' * 3 + '/' + lib + aid + '/' + lib + aid + '.pdf')
    )


class DocAlephCardKind(models.TextChoices):
    SYNOPSIS = 'synopsis'
    DISSERTATION = 'dissertation'


class DocAlephCard(DatesModelBase):
    UPLOAD_TO = Path('docs-cards-files')

    doc = models.ForeignKey('d11.Doc', on_delete=models.CASCADE, related_name='aleph_cards', verbose_name=_('запись'))
    kind = models.CharField(max_length=50, choices=DocAlephCardKind.choices, verbose_name=_('тип'))
    file = models.FileField(upload_to=doc_aleph_card_upload_to, null=True, blank=True, verbose_name=_('файл'))
    aleph_id = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Алеф ID'))
    aleph_fields_json = models.JSONField(default=dict, verbose_name=_('доп. данные'))

    class Meta:
        unique_together = [
            ['doc', 'kind']
        ]
        verbose_name = _('карточка Алеф')
        verbose_name_plural = _('карточки Алеф')

    class QuerySet(models.QuerySet):
        pass

    class Manager(models.Manager.from_queryset(QuerySet)):
        pass

    objects = Manager()

    @transaction.atomic
    def file_set(self, path: Optional[Path] = None) -> Optional[Path]:
        if not path:
            doc_file_field_name = {
                DocAlephCardKind.SYNOPSIS: 'autoref_file',
                DocAlephCardKind.DISSERTATION: 'disser_file',
            }.get(self.kind)
            for doc_filed_value in self.doc.files_values.all():
                if doc_filed_value.field.name == doc_file_field_name:
                    path = doc_filed_value.value.path
                    break
        if not path:
            return
        self.file.name = str(self.file_path)
        file_path = Path(self.file.path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy(path, self.file.path)
        except FileNotFoundError as e:
            if not settings.DEBUG:
                raise e
        self.save()

    def __str__(self):
        return f'{self.kind} – {self.id} / {self.doc_id}'

    @property
    def file_path(self) -> Optional[Path]:
        if not self.aleph_id:
            return
        return Path(doc_aleph_card_upload_to(self, '1.pdf'))


class DocAlephCardFilesExport(DatesModelBase):
    cards = models.ManyToManyField('d11.DocAlephCard', related_name='files_exports')
    is_all = models.BooleanField(default=False)
    extra = models.JSONField(default=dict)

    class Meta:
        verbose_name = _('экспорт файлов карточек Алеф')
        verbose_name_plural = _('экспорты файлов карточек Алеф')

    @property
    def docs_count(self) -> int:
        return len(set(card.doc_id for card in self.cards.all()))

    @property
    def cards_count(self) -> int:
        return len(self.cards.all())
