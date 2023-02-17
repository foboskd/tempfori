from django.core.management.base import BaseCommand

from main.services.email_notification import EmailNotificationService


class Command(BaseCommand):
    def handle(self, *args, **options):
        EmailNotificationService.make_instance_and_send_emails()
