from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0008_country_and_fixed_course_fields')]
    operations = [
        migrations.AlterField(
            model_name='university',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='universities', to='platform_app.country'),
        ),
    ]
