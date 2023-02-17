from typing import Type

from django.db import models
from django.utils.translation import gettext_lazy as _

from d11.collector import registry as collector_registry, CollectorAbstract

__all__ = [
    'Source'
]


class Source(models.Model):
    COLLECTOR_CLASS_CHOICES = [
        [k, v.verbose_name]
        for k, v in collector_registry.items()
    ]
    label = models.CharField(max_length=1000, unique=True, verbose_name=_('название'))
    collector_class = models.CharField(max_length=100, choices=COLLECTOR_CLASS_CHOICES, verbose_name=_('класс'))
    is_enabled = models.BooleanField(default=True, verbose_name=_('включен'))
    attributes = models.JSONField(null=True, blank=True, verbose_name=_('доп. данные'))

    class Meta:
        ordering = ['id']
        verbose_name = _('источник')
        verbose_name_plural = _('источники')

    def __str__(self):
        return self.label

    def get_collector_class(self) -> Type[CollectorAbstract]:
        return collector_registry[self.collector_class]

    def get_collector(self, **kwargs) -> CollectorAbstract:
        return self.get_collector_class()(source=self, **kwargs)
