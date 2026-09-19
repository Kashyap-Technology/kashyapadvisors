from django.db import migrations


FIELDS = [
    ('study-location','Study location','fact'),
    ('study-mode','Study mode','fact'),
    ('nominal-duration','Nominal duration','fact'),
    ('study-language','Study language','fact'),
    ('awards','Awards','fact'),
    ('course-code','Course code','fact'),
    ('tuition-fee','Tuition fee','fact'),
    ('application-fee','Application fee','fact'),
    ('deposit','Deposit','fact'),
    ('entry-qualification','Entry qualification','section'),
    ('language-requirements','Language requirements','section'),
    ('other-requirements','Other requirements','section'),
    ('required-documents','Required documents','section'),
    ('more-information','More information','section'),
]


def seed(apps,schema_editor):
    Field=apps.get_model('platform_app','CourseField')
    for order,(key,label,presentation) in enumerate(FIELDS):
        Field.objects.get_or_create(key=key,defaults={'label':label,'presentation':presentation,'order':order*10})


class Migration(migrations.Migration):
    dependencies=[('platform_app','0002_coursefield_admissioncall_department_and_more')]
    operations=[migrations.RunPython(seed,migrations.RunPython.noop)]
