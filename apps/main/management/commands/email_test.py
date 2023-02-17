from django.core.management.base import BaseCommand

from main.msg import get_email_message_by_template


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+')

    def handle(self, *args, **options):
        msg = get_email_message_by_template('test')
        msg.to = options['email']
        msg.send()
