import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Create or promote a Django admin user from Render environment variables.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-password',
            action='store_true',
            help='Reset the existing user password from DJANGO_SUPERUSER_PASSWORD.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
        if not username or not email or not password:
            raise CommandError(
                'Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, '
                'and DJANGO_SUPERUSER_PASSWORD before running provision_admin.'
            )
        if len(password) < 12:
            raise CommandError('DJANGO_SUPERUSER_PASSWORD must contain at least 12 characters.')

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True, 'is_active': True},
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        if created or options['reset_password']:
            user.set_password(password)
        user.save(update_fields=['email', 'is_staff', 'is_superuser', 'is_active', 'password'])
        action = 'Created' if created else 'Promoted'
        self.stdout.write(self.style.SUCCESS(f'{action} admin user {username!r}.'))
