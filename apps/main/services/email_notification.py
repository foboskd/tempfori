from pathlib import Path
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models import Q, F

from d11.models import Doc
from d11.services.excel_report import create_excel_report
from main.models import EmailNotification
from main.msg import get_email_message_by_template


class EmailNotificationService:
    instance: EmailNotification

    def __init__(self, instance: EmailNotification):
        self.instance = instance

    @classmethod
    @transaction.atomic
    def make_instance_and_send_emails(cls) -> Optional[EmailNotification]:
        instance = cls.make_instance()
        if not instance:
            return
        service = cls(instance)
        service.generate_xlsx()
        service.send_emails()
        return service.instance

    def send_emails(self):
        email_msg = get_email_message_by_template('import-notification')
        email_msg.attach_file(self.instance.excel_report.path, 'application/vnd.ms-excel')
        email_msg.to = settings.NOTICE_EMAILS
        email_msg.send()

    def generate_xlsx(self):
        excel_workbook = create_excel_report(self.instance.docs.prefetch_related(
            *Doc.objects.get_queryset_prefetch_related()
        ))
        self.instance.excel_report.name = (
            self.instance._meta.get_field('excel_report')
                .generate_filename(self.instance, '1.xlsx')
        )
        path = Path(self.instance.excel_report.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        excel_workbook.save(self.instance.excel_report.path)
        self.instance.save()

    @classmethod
    @transaction.atomic
    def make_instance(cls) -> Optional[EmailNotification]:
        docs_queryset = cls.get_docs_queryset()
        if not docs_queryset.count():
            return
        instance = EmailNotification(emails=settings.NOTICE_EMAILS)
        instance.save()
        instance.docs.add(*docs_queryset)
        return instance

    @classmethod
    def get_docs_queryset(cls) -> Doc.QuerySet:
        return Doc.objects.distinct().filter(
            Q(
                Q(aleph_cards__created_at__gt=F('emails_notifications__created_at'))
                | Q(emails_notifications__created_at__isnull=True)
            ),
            aleph_cards__isnull=False,
        ).prefetch_related(
            *Doc.objects.get_queryset_prefetch_related()
        )
