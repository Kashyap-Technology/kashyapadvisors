from django.db import migrations, models
import django.db.models.deletion


def copy_existing_sections(apps, schema_editor):
    Article = apps.get_model('platform_app', 'Article')
    ArticleSection = apps.get_model('platform_app', 'ArticleSection')
    for article in Article.objects.all():
        for order, section in enumerate(article.sections or []):
            if not isinstance(section, dict) or not section.get('heading'):
                continue
            ArticleSection.objects.create(
                article=article,
                heading=section.get('heading', ''),
                body=section.get('body', ''),
                kind=section.get('kind', 'guidance'),
                source_url=section.get('source_url', ''),
                order=order,
            )


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0004_course_owned_fields')]
    operations = [
        migrations.CreateModel(
            name='ArticleSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(help_text='A clear heading for this part of the article.', max_length=240)),
                ('body', models.TextField(help_text='Write normally. Use a blank line between paragraphs.')),
                ('kind', models.CharField(choices=[('guidance', 'Guidance / advice'), ('official', 'Official information'), ('estimate', 'Estimate / budget')], default='guidance', max_length=20)),
                ('source_url', models.URLField(blank=True, help_text='Optional link to the official source for this block.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_sections', to='platform_app.article')),
            ],
            options={'ordering': ['order', 'pk'], 'verbose_name': 'Blog section', 'verbose_name_plural': 'Blog sections'},
        ),
        migrations.RunPython(copy_existing_sections, migrations.RunPython.noop),
    ]
