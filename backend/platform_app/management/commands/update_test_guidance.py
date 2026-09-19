from django.core.management.base import BaseCommand
from django.db import transaction
from platform_app.models import Page
from platform_app.test_content import TEST_PAGES, REVIEWED


class Command(BaseCommand):
    help = 'Refresh only the five test guides, preserving their URLs and publication status.'

    @transaction.atomic
    def handle(self, *args, **options):
        for order, data in enumerate(TEST_PAGES):
            page, created = Page.objects.get_or_create(
                slug=data['slug'], defaults={'kind': 'test', 'published': True})
            if page.kind != 'test':
                raise ValueError(f"Refusing to change non-test page: {page.slug}")
            for field in ('title', 'summary', 'sections', 'source_url'):
                setattr(page, field, data[field])
            page.reviewed_at = REVIEWED
            page.order = order
            page.save()
        self.stdout.write(self.style.SUCCESS('Updated five test guides; URLs and existing publication choices preserved.'))
