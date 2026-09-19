from django.db import migrations, models
import django.db.models.deletion


def copy_existing_sections(apps, schema_editor):
    Page = apps.get_model('platform_app', 'Page')
    PageSection = apps.get_model('platform_app', 'PageSection')
    for page in Page.objects.all():
        for order, section in enumerate(page.sections or []):
            if not isinstance(section, dict) or not section.get('heading'):
                continue
            PageSection.objects.create(
                page=page,
                heading=section.get('heading', ''),
                body=section.get('body', ''),
                kind=section.get('kind', 'guidance'),
                source_url=section.get('source_url', ''),
                order=order,
            )


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0009_require_university_country')]
    operations = [
        migrations.CreateModel(
            name='PageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(help_text='Section heading, for example: Our mission.', max_length=240)),
                ('body', models.TextField(help_text='Write the section content normally. Use a blank line between paragraphs.')),
                ('kind', models.CharField(choices=[('guidance', 'Guidance / advice'), ('official', 'Official information'), ('estimate', 'Estimate / budget')], default='guidance', max_length=20)),
                ('source_url', models.URLField(blank=True, help_text='Optional official source link for this section.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_sections', to='platform_app.page')),
            ],
            options={'ordering': ['order', 'pk'], 'verbose_name': 'Page section', 'verbose_name_plural': 'Page sections'},
        ),
        migrations.RunPython(copy_existing_sections, migrations.RunPython.noop),
    ]
