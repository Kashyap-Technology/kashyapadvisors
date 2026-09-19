from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0013_verified_padua_courses')]
    operations = [
        migrations.AddField(
            model_name='university',
            name='logo_url',
            field=models.URLField(
                blank=True,
                help_text='Official university logo or favicon URL used when no uploaded logo is available.',
            ),
        ),
    ]
