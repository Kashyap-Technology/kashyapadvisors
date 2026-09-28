import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from platform_app.models import Course, University


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'italy_courses.json'


class Command(BaseCommand):
    help = 'Synchronize the published university and course catalog from the verified local source.'

    def add_arguments(self, parser):
        parser.add_argument('--data-path', type=Path, default=DEFAULT_DATA_PATH)
        parser.add_argument('--include-pending', action='store_true', help='Keep pending source rows unpublished for review.')
        parser.add_argument('--deactivate-stale', action='store_true', help='Unpublish courses no longer present in the source file.')

    @transaction.atomic
    def handle(self, *args, **options):
        path = options['data_path']
        if not path.exists():
            raise CommandError(f'Catalog data file not found: {path}')

        data = json.loads(path.read_text(encoding='utf-8'))
        source_slugs = {
            item['slug'] for item in data.get('courses', [])
            if item.get('verified') or options['include_pending']
        }
        if not source_slugs:
            raise CommandError('No course records are available in the source file.')

        # These two idempotent commands are the same sequence used to build the
        # local catalog. Running it against the production DATABASE_URL makes
        # the remote database reproducible from versioned source data.
        call_command('seed_content')
        call_command(
            'import_verified_courses',
            data_path=path,
            include_pending=options['include_pending'],
        )

        stale_count = 0
        if options['deactivate_stale']:
            stale_count = Course.objects.filter(published=True).exclude(slug__in=source_slugs).update(published=False)

        self.stdout.write(self.style.SUCCESS(
            f'Synchronized {University.objects.filter(published=True).count()} published universities and '
            f'{Course.objects.filter(published=True).count()} published courses. '
            f'Unpublished stale courses: {stale_count}.'
        ))
