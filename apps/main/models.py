from pathlib import Path

from django.db import models
from django.contrib.postgres.fields import ArrayField

from project.contrib.db.models import DatesModelBase


def email_notification_upload_to(instance: 'EmailNotification', filename: str) -> str:
    return str(
        Path('emails')
        / instance.id_verbose[:3]
        / instance.id_verbose[3:6]
        / f'{instance.id_verbose}{Path(filename).suffix}'
    )


class EmailNotification(DatesModelBase):
    emails = ArrayField(models.EmailField(), null=True, blank=True)
    excel_report = models.FileField(upload_to=email_notification_upload_to, null=True, blank=True)
    docs = models.ManyToManyField('d11.Doc', related_name='emails_notifications', blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def id_verbose(self) -> str:
        return str(self.id).zfill(9)

    @property
    def docs_count(self) -> int:
        return len(self.docs.all())
