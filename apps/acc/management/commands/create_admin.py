from django.core.management.base import BaseCommand

from acc.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        email = 'atlantij@gmail.com'
        user = User.objects.filter(email=email).first()
        is_user_created = False
        if not user:
            is_user_created = True
            user = User(email=email)
        user.first_name = 'Alexey'
        user.last_name = 'Baranov'
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        if is_user_created:
            user.set_password('not11pass;not11pass;not11pass')
            user.save()
