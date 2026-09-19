from django.db import migrations, models
import django.db.models.deletion


def assign_existing_universities(apps, schema_editor):
    Country = apps.get_model('platform_app', 'Country')
    University = apps.get_model('platform_app', 'University')
    italy, _ = Country.objects.get_or_create(name='Italy', defaults={'slug':'italy','code':'IT','published':True})
    University.objects.filter(country__isnull=True).update(country=italy)
    Course = apps.get_model('platform_app', 'Course')
    for course in Course.objects.all():
        course.tuition_fee = course.tuition
        course.study_language = 'English' if course.english_taught else ''
        course.save(update_fields=['tuition_fee','study_language'])


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0007_career_vacancy_fields')]
    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('code', models.CharField(help_text='Two-letter country code, for example IT.', max_length=2, unique=True)),
                ('published', models.BooleanField(default=True)),
            ],
            options={'ordering':['name']},
        ),
        migrations.AddField(model_name='university',name='country',field=models.ForeignKey(blank=False,null=True,on_delete=django.db.models.deletion.PROTECT,related_name='universities',to='platform_app.country')),
        migrations.AddField(model_name='course',name='degree_class_code',field=models.CharField(blank=True,max_length=80)),
        migrations.AddField(model_name='course',name='study_location',field=models.CharField(blank=True,max_length=240)),
        migrations.AddField(model_name='course',name='course_type',field=models.CharField(blank=True,help_text='For example: Bachelor’s degree, full-time.',max_length=160)),
        migrations.AddField(model_name='course',name='nominal_duration',field=models.CharField(blank=True,help_text='For example: 3 years (180 ECTS).',max_length=100)),
        migrations.AddField(model_name='course',name='study_language',field=models.CharField(blank=True,max_length=120)),
        migrations.AddField(model_name='course',name='application_fee',field=models.CharField(blank=True,max_length=200)),
        migrations.AddField(model_name='course',name='pre_enrollment_fee',field=models.CharField(blank=True,max_length=200)),
        migrations.AddField(model_name='course',name='tuition_fee',field=models.CharField(blank=True,max_length=200)),
        migrations.AddField(model_name='course',name='cent_requirements',field=models.TextField(blank=True)),
        migrations.AddField(model_name='course',name='language_requirements',field=models.TextField(blank=True)),
        migrations.AddField(model_name='course',name='other_requirements',field=models.TextField(blank=True)),
        migrations.AddField(model_name='course',name='studies_commence',field=models.DateField(blank=True,null=True)),
        migrations.AddField(model_name='course',name='more_information',field=models.URLField(blank=True)),
        migrations.AddField(model_name='course',name='entry_qualification',field=models.TextField(blank=True)),
        migrations.AddField(model_name='course',name='course_link',field=models.URLField(blank=True)),
        migrations.AddField(model_name='course',name='additional_info',field=models.TextField(blank=True)),
        migrations.RunPython(assign_existing_universities, migrations.RunPython.noop),
    ]
