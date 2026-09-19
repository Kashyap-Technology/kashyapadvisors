from django.db import migrations, models
import django.db.models.deletion


def copy_existing_social_links(apps, schema_editor):
    SiteSettings = apps.get_model('platform_app', 'SiteSettings')
    SocialLink = apps.get_model('platform_app', 'SocialLink')
    for settings in SiteSettings.objects.all():
        for order, link in enumerate(settings.social_links or []):
            if not isinstance(link, dict) or not link.get('label') or not link.get('url'):
                continue
            SocialLink.objects.create(settings=settings,label=link['label'],url=link['url'],order=order,active=True)


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0010_page_sections')]
    operations = [
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(help_text='For example: Facebook, Instagram or TikTok.', max_length=80)),
                ('url', models.URLField(help_text='Paste the complete https:// link.')),
                ('order', models.PositiveIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_link_items', to='platform_app.sitesettings')),
            ],
            options={'ordering':['order','pk'],'verbose_name':'Social link','verbose_name_plural':'Social links'},
        ),
        migrations.RunPython(copy_existing_social_links, migrations.RunPython.noop),
    ]
