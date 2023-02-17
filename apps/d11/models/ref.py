from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    'RefType',
    'Ref',
]


class RefType(models.TextChoices):
    KIND = 'kind', _('Тип диссертации')
    INDUSTRY = 'industry', _('Отрасль науки')


class Ref(models.Model):
    type = models.CharField(max_length=20, choices=RefType.choices)
    from_what = models.CharField(max_length=500)
    to_what = models.CharField(max_length=500)

    class Meta:
        ordering = ['type', 'from_what']
        unique_together = [
            'type', 'from_what',
        ]
        verbose_name = _('замена для Алефа')
        verbose_name_plural = _('замены для Алефа')

    class Manager(models.Manager):
        def get_by_from_what(self, ref_type: RefType, from_what: str) -> Optional['Ref']:
            return self.get_queryset().get(type=ref_type, from_what__iexact=from_what)

    objects = Manager()

    def __str__(self):
        return f'{self.from_what} –> {self.to_what}'
