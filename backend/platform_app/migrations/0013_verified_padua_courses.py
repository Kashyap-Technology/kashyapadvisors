from datetime import date

from django.db import migrations


REVIEWED_AT = date(2026, 9, 19)

COURSES = [
    {
        'title': 'Animal Care',
        'slug': 'animal-care',
        'department': 'Department of Comparative Biomedicine and Food Science',
        'degree': "Bachelor's degree",
        'discipline': 'Animal science and welfare',
        'degree_class_code': '',
        'study_location': 'Italy, Legnaro (Padua)',
        'course_type': "Bachelor's degree, full-time",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://agrariamedicinaveterinaria.unipd.it/en/courses/bachelors-first-cycle-and-masters-second-cycle-degrees/animal-care',
        'summary': 'A bachelor’s programme focused on animal management, welfare, behaviour, conservation and husbandry practices.',
    },
    {
        'title': 'Biology of Human and Environmental Health',
        'slug': 'biology-human-environmental-health',
        'department': 'Department of Biomedical Sciences',
        'degree': "Bachelor's degree",
        'discipline': 'Biology and environmental health',
        'degree_class_code': '',
        'study_location': 'Italy, Padua',
        'course_type': "Bachelor's degree, full-time",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://www.unipd.it/en/biology-human-environmental-health',
        'summary': 'An interdisciplinary programme covering the biological foundations of human health and interactions between people and the environment.',
    },
    {
        'title': 'Earth and Climate Dynamics',
        'slug': 'earth-climate-dynamics',
        'department': 'Department of Geosciences',
        'degree': "Bachelor's degree",
        'discipline': 'Earth sciences and climate',
        'degree_class_code': 'L-34',
        'study_location': 'Italy, Padua',
        'course_type': "Bachelor's degree, full-time",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://www.geoscienze.unipd.it/en/courses/bachelors-degree-earth-and-climate-dynamics-english',
        'summary': 'An English-taught bachelor’s programme in Earth system sciences, including solid Earth, oceans, climate, atmosphere and biosphere dynamics.',
    },
    {
        'title': 'Economics, Governance and Decision-Making',
        'slug': 'economics-governance-and-decision-making',
        'department': 'Department of Economics and Management Marco Fanno',
        'degree': "Bachelor's degree",
        'discipline': 'Economics and governance',
        'degree_class_code': 'L-33',
        'study_location': 'Italy, Padua',
        'course_type': "Bachelor's degree, full-time",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://www.economia.unipd.it/en/Bachelor%27s-degree-EGDM/bachelor%E2%80%99s-degree-economics-governance-and-decision-making',
        'summary': 'An English-taught bachelor’s programme combining economics, political science, philosophy and law with methodological and ethical reasoning.',
    },
    {
        'title': 'Information Engineering',
        'slug': 'information-engineering',
        'department': 'Department of Information Engineering',
        'degree': "Bachelor's degree",
        'discipline': 'Information engineering',
        'degree_class_code': 'L-8',
        'study_location': 'Italy, Padua',
        'course_type': "Bachelor's degree, full-time",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://www.unipd.it/en/corsi-laurea-lingua-inglese',
        'summary': 'An English-taught bachelor’s programme in information engineering listed in the University of Padua’s official English degree catalogue.',
    },
    {
        'title': 'Psychological Science',
        'slug': 'psychological-science',
        'department': 'Department of General Psychology',
        'degree': "Bachelor's degree",
        'discipline': 'Psychology',
        'degree_class_code': '',
        'study_location': 'Italy, Padua',
        'course_type': "Bachelor's degree, full-time",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://apply.unipd.it/courses/course/27-psychological-science',
        'summary': 'An English-taught bachelor’s programme covering foundational psychological theory, research methods, brain and behaviour, development and social psychology.',
    },
    {
        'title': 'Techniques and Methods in Psychological Science',
        'slug': 'techniques-methods-psychological-science',
        'department': 'Department of General Psychology',
        'degree': "Bachelor's degree",
        'discipline': 'Psychology',
        'degree_class_code': 'L-24 R',
        'study_location': 'Italy, Padua',
        'course_type': "Bachelor's degree, online-delivered with exams in Padua",
        'nominal_duration': '3 years (180 ECTS)',
        'study_language': 'English',
        'source_url': 'https://www.unipd.it/corsi-di-laurea/techniques-and-methods-psychological-science',
        'summary': 'An English-taught psychology bachelor’s programme delivered online, with exams held in person at the University of Padua.',
    },
]


def seed_verified_courses(apps, schema_editor):
    University = apps.get_model('platform_app', 'University')
    Department = apps.get_model('platform_app', 'Department')
    Course = apps.get_model('platform_app', 'Course')

    # Some lightweight test databases do not load the production university
    # catalogue. Keep the data migration safe in those environments; the
    # production database contains this canonical university record.
    try:
        university = University.objects.get(slug='university-of-padua')
    except University.DoesNotExist:
        return

    for item in COURSES:
        department, _ = Department.objects.get_or_create(
            university=university,
            title=item['department'],
            defaults={'published': True},
        )
        department.published = True
        department.save(update_fields=['published'])
        values = {
            **{key: item[key] for key in (
                'title', 'summary', 'degree', 'discipline', 'degree_class_code',
                'study_location', 'course_type', 'nominal_duration', 'study_language',
                'source_url',
            )},
            'university': university,
            'department': department,
            'english_taught': True,
            'published': True,
            'reviewed_at': REVIEWED_AT,
            'course_link': item['source_url'],
            'additional_info': 'Verified against the official University of Padua source on 2026-09-19. Fees and admission deadlines are intentionally omitted until confirmed from the current official call.',
        }
        course, _ = Course.objects.update_or_create(slug=item['slug'], defaults=values)
        if course.department_id != department.pk:
            course.department = department
            course.save(update_fields=['department'])


def remove_verified_courses(apps, schema_editor):
    Course = apps.get_model('platform_app', 'Course')
    Course.objects.filter(slug__in=[item['slug'] for item in COURSES]).delete()


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0012_official_updates')]
    operations = [migrations.RunPython(seed_verified_courses, remove_verified_courses)]
