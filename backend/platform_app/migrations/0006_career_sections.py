from django.db import migrations, models
import django.db.models.deletion


def copy_existing_sections(apps, schema_editor):
    Career = apps.get_model('platform_app', 'Career')
    CareerSection = apps.get_model('platform_app', 'CareerSection')
    for career in Career.objects.all():
        for order, section in enumerate(career.sections or []):
            if not isinstance(section, dict) or not section.get('heading'):
                continue
            CareerSection.objects.create(
                career=career,
                heading=section.get('heading', ''),
                body=section.get('body', ''),
                kind=section.get('kind', 'guidance'),
                source_url=section.get('source_url', ''),
                order=order,
            )


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0005_article_sections')]
    operations = [
        migrations.CreateModel(
            name='CareerSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(help_text='For example: What you will do or How to apply.', max_length=240)),
                ('body', models.TextField(help_text='Write normally. Use a blank line between paragraphs.')),
                ('kind', models.CharField(choices=[('guidance', 'Guidance / advice'), ('official', 'Official information'), ('estimate', 'Estimate / budget')], default='guidance', max_length=20)),
                ('source_url', models.URLField(blank=True, help_text='Optional link to the official source for this block.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('career', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='career_sections', to='platform_app.career')),
            ],
            options={'ordering': ['order', 'pk'], 'verbose_name': 'Career section', 'verbose_name_plural': 'Career sections'},
        ),
        migrations.RunPython(copy_existing_sections, migrations.RunPython.noop),
    ]
