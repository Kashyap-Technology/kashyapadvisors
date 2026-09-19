import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from platform_app.models import Country, Course, CourseFieldValue, Department, Region, University


DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'italy_courses.json'


class Command(BaseCommand):
    help = 'Bulk import course records that passed the official-source audit.'

    def add_arguments(self, parser):
        parser.add_argument('--data-path', type=Path, default=DATA_PATH)
        parser.add_argument('--include-pending', action='store_true', help='Import pending rows as unpublished review records.')

    @transaction.atomic
    def handle(self, *args, **options):
        path = options['data_path']
        if not path.exists():
            raise CommandError(f'Catalog data file not found: {path}')
        data = json.loads(path.read_text(encoding='utf-8'))
        records = [course for course in data.get('courses', []) if course.get('verified') or options['include_pending']]
        if not records:
            raise CommandError('No verified course records are available for import.')

        italy, _ = Country.objects.get_or_create(
            code='IT',
            defaults={'name': 'Italy', 'slug': 'italy', 'published': True},
        )
        if not italy.published:
            italy.published = True
            italy.save(update_fields=['published'])

        universities_by_slug = {}
        for item in data.get('universities', []):
            region = Region.objects.filter(code=item['region_code']).first()
            if region is None:
                region = Region.objects.create(
                    title=item['city'],
                    slug=slugify(item['city']),
                    summary='',
                    published=True,
                    code=item['region_code'],
                    cities=[item['city']],
                )
            university, _ = University.objects.get_or_create(
                slug=item['slug'],
                defaults={
                    'title': item['name'],
                    'country': italy,
                    'region': region,
                    'city': item['city'],
                    'website': item['website'],
                    'published': True,
                    'summary': f"{item['name']} in {item['city']}, Italy.",
                    'source_url': item['website'],
                },
            )
            university.title = item['name']
            university.country = italy
            university.region = region
            university.city = item['city']
            university.website = item['website']
            university.source_url = item['website']
            university.published = True
            if item.get('logo_url'):
                university.logo_url = item['logo_url']
            university.save(update_fields=['title', 'country', 'region', 'city', 'website', 'source_url', 'published', 'logo_url'])
            universities_by_slug[item['slug']] = university

        department_keys = {(course['university_slug'], course['department']) for course in records}
        departments_by_key = {}
        for university_slug, title in department_keys:
            university = universities_by_slug[university_slug]
            department, _ = Department.objects.get_or_create(
                university=university,
                title=title[:240],
                defaults={'published': True, 'website': university.website},
            )
            if not department.published or not department.website:
                department.published = True
                department.website = department.website or university.website
                department.save(update_fields=['published', 'website'])
            departments_by_key[(university_slug, title)] = department

        existing = {course.slug: course for course in Course.objects.filter(slug__in=[c['slug'] for c in records])}
        new_courses = []
        update_courses = []
        fields_by_course = defaultdict(list)
        for item in records:
            university = universities_by_slug[item['university_slug']]
            department = departments_by_key[(item['university_slug'], item['department'])]
            reviewed_at = date.fromisoformat(item['verified_at']) if item.get('verified_at') else None
            source_url = item.get('verified_source_url') or item.get('source_url', '')
            defaults = {
                'title': item['title'][:240],
                'summary': item.get('summary', f"{item['title']} at {university.title}.")[:10000],
                'university': university,
                'department': department,
                'degree': item['degree'][:40],
                'discipline': item['discipline'][:100],
                'english_taught': 'english' in item.get('study_language', '').lower(),
                'degree_class_code': item.get('degree_class_code', '')[:80],
                'study_location': item.get('study_location', '')[:240],
                'course_type': item.get('course_type', '')[:160],
                'nominal_duration': item.get('nominal_duration', '')[:100],
                'study_language': item.get('study_language', '')[:120],
                'application_fee': item.get('application_fee', '')[:200],
                'pre_enrollment_fee': item.get('pre_enrollment_fee', '')[:200],
                'tuition_fee': item.get('tuition_fee', '')[:200],
                'cent_requirements': item.get('cent_requirements', ''),
                'language_requirements': item.get('language_requirements', ''),
                'other_requirements': item.get('other_requirements', ''),
                'entry_qualification': item.get('entry_qualification', ''),
                'more_information': item.get('more_information', '')[:10000],
                'course_link': item.get('course_link', '')[:10000],
                'additional_info': item.get('additional_info', ''),
                'source_url': source_url,
                'reviewed_at': reviewed_at,
                'published': bool(item.get('verified')),
            }
            if item.get('studies_commence'):
                # The workbook contains mixed prose and dates. Preserve prose in
                # the extra fields instead of inventing a DateField value.
                fields_by_course[item['slug']].append({'label': 'Studies commence', 'value': item['studies_commence']})
            course = existing.get(item['slug'])
            if course is None:
                new_courses.append(Course(slug=item['slug'], **defaults))
            else:
                for key, value in defaults.items():
                    setattr(course, key, value)
                update_courses.append(course)
            for field in item.get('extra_fields', []):
                fields_by_course[item['slug']].append(field)
            verification = item.get('verified_source_url') or item.get('source_url')
            if verification:
                fields_by_course[item['slug']].append({
                    'label': 'Official source verification',
                    'value': f"Verified against the official source on {item.get('verified_at') or 'the supplied source audit'}: {verification}",
                })

        Course.objects.bulk_create(new_courses, batch_size=250)
        Course.objects.bulk_update(update_courses, fields=list(defaults.keys()), batch_size=250)
        all_courses = {course.slug: course for course in Course.objects.filter(slug__in=[c['slug'] for c in records])}

        existing_values = {
            (value.course_id, value.label): value
            for value in CourseFieldValue.objects.filter(course_id__in=[course.pk for course in all_courses.values()])
        }
        new_values = []
        update_values = []
        for slug, raw_fields in fields_by_course.items():
            course = all_courses[slug]
            merged = {}
            for field in raw_fields:
                label = (field.get('label') or 'Additional source detail').strip()[:160]
                value = (field.get('value') or '').strip()
                if value:
                    merged[label] = f"{merged[label]}\n\n{value}" if label in merged else value
            for order, (label, value) in enumerate(merged.items()):
                key = (course.pk, label)
                current = existing_values.get(key)
                if current is None:
                    new_values.append(CourseFieldValue(
                        course=course,
                        label=label,
                        value=value,
                        presentation='section' if len(value) > 180 else 'fact',
                        order=order,
                        active=True,
                        source_url=course.source_url,
                        link_label='Official source',
                    ))
                else:
                    current.value = value
                    current.order = order
                    current.source_url = course.source_url
                    current.active = True
                    update_values.append(current)
        CourseFieldValue.objects.bulk_create(new_values, batch_size=500)
        CourseFieldValue.objects.bulk_update(update_values, fields=['value', 'order', 'source_url', 'active'], batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(records)} course records ({len(new_courses)} new, {len(update_courses)} updated), "
            f"{len(new_values)} new course fields and {len(data.get('universities', []))} universities."
        ))
        pending = data.get('verification_summary', {}).get('pending_courses', 0)
        if pending:
            self.stdout.write(self.style.WARNING(f'{pending} workbook rows remain pending verification and were not published.'))
