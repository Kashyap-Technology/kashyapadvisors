import re
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError

from platform_app.models import Course, Department, University


DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'italy_courses.json'
URL_PATTERN = re.compile(r'https?://[^\s|]+', re.IGNORECASE)
REQUIREMENT_FIELDS = ('cent_requirements', 'language_requirements', 'other_requirements', 'entry_qualification')


def valid_url(value):
    parsed = urlparse(value.strip())
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


class Command(BaseCommand):
    help = 'Audit published course requirements, source links and university relationships.'

    def add_arguments(self, parser):
        parser.add_argument('--data-path', type=Path, default=DEFAULT_DATA_PATH)
        parser.add_argument('--strict', action='store_true', help='Exit with an error when a published record fails an audit check.')

    def handle(self, *args, **options):
        courses = Course.objects.filter(published=True).select_related('university', 'department')
        source_path = options['data_path']
        expected = set()
        if source_path.exists():
            import json
            expected = {x['slug'] for x in json.loads(source_path.read_text(encoding='utf-8')).get('courses', []) if x.get('verified')}

        missing_sources = [course.slug for course in courses if not course.source_url or not valid_url(course.source_url)]
        missing_review_dates = [course.slug for course in courses if not course.reviewed_at]
        broken_relationships = [course.slug for course in courses if not course.department_id or course.department.university_id != course.university_id]
        malformed_links = []
        for course in courses:
            for field in ('course_link', 'more_information'):
                value = getattr(course, field)
                urls = URL_PATTERN.findall(value) if value else []
                # These legacy URLField values may contain several pipe-separated
                # links. A non-empty value with no scheme-qualified URL is still
                # malformed, rather than silently passing the audit.
                if value and (not urls or any(not valid_url(url) for url in urls)):
                    malformed_links.append(f'{course.slug}:{field}')
        missing_requirements = [course.slug for course in courses if not any(getattr(course, field) for field in REQUIREMENT_FIELDS)]
        source_missing_in_db = sorted(expected - set(courses.values_list('slug', flat=True)))

        self.stdout.write(f'Published universities: {University.objects.filter(published=True).count()}')
        self.stdout.write(f'Published departments: {Department.objects.filter(published=True).count()}')
        self.stdout.write(f'Published courses: {courses.count()}')
        self.stdout.write(f'Courses with at least one requirement field: {courses.count() - len(missing_requirements)}')
        self.stdout.write(f'Courses with official source and review date: {courses.count() - len(set(missing_sources + missing_review_dates))}')
        self.stdout.write(f'Malformed source/course links: {len(malformed_links)}')
        self.stdout.write(f'Broken university/department relationships: {len(broken_relationships)}')
        self.stdout.write(f'Verified source rows missing from database: {len(source_missing_in_db)}')

        if missing_sources:
            self.stdout.write(self.style.WARNING(f'Missing or invalid source URLs (first 10): {", ".join(missing_sources[:10])}'))
        if missing_review_dates:
            self.stdout.write(self.style.WARNING(f'Missing review dates (first 10): {", ".join(missing_review_dates[:10])}'))
        if malformed_links:
            self.stdout.write(self.style.WARNING(f'Malformed links (first 10): {", ".join(malformed_links[:10])}'))
        if broken_relationships:
            self.stdout.write(self.style.ERROR(f'Broken relationships (first 10): {", ".join(broken_relationships[:10])}'))
        if source_missing_in_db:
            self.stdout.write(self.style.ERROR(f'Missing source rows (first 10): {", ".join(source_missing_in_db[:10])}'))

        failures = missing_sources + missing_review_dates + malformed_links + broken_relationships + source_missing_in_db
        if options['strict'] and failures:
            raise CommandError(f'Course catalog audit failed with {len(failures)} issue(s).')
