from django.db import models
from django.utils.translation import gettext_lazy as _

from project.contrib.db.models import DatesModelBase

__all__ = [
    'CollectorImport',
]


class CollectorImport(DatesModelBase):
    collector_name = models.CharField(max_length=1000, verbose_name=_('тип импорта'))
    docs = models.ManyToManyField('d11.Doc', related_name='+', verbose_name=_('записи'))
    extra = models.JSONField(default=dict, verbose_name=_('доп. данные'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('импорт из источника')
        verbose_name_plural = _('импорт из источников')

    @property
    def docs_affected_count(self) -> int:
        return len(self.docs.all())

    @property
    def docs_created_count(self) -> int:
        return self.extra.get('docs_created') or 0

    @property
    def docs_updated_count(self) -> int:
        return self.extra.get('docs_updated') or 0

    @property
    def docs_total_count(self) -> int:
        return self.extra.get('total_count') or 0
