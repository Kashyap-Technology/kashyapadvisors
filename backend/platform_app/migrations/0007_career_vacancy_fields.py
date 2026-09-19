from django.db import migrations, models


def convert_career_sections(apps, schema_editor):
    Career = apps.get_model('platform_app', 'Career')
    for career in Career.objects.all():
        sections = career.sections or []
        description = []
        requirements = []
        instructions = []
        for section in sections:
            if not isinstance(section, dict):
                continue
            heading = (section.get('heading') or '').lower()
            body = section.get('body') or ''
            if 'apply' in heading:
                instructions.append(body)
            elif 'require' in heading:
                requirements.append(body)
            else:
                description.append(body)
        career.job_description = '\n\n'.join(description)
        career.requirements = '\n\n'.join(requirements)
        career.application_instructions = '\n\n'.join(instructions)
        career.status = 'open' if career.published else 'closed'
        career.save(update_fields=['job_description','requirements','application_instructions','status'])


class Migration(migrations.Migration):
    dependencies = [('platform_app', '0006_career_sections')]
    operations = [
        migrations.AddField(model_name='career',name='salary',field=models.CharField(blank=True,help_text='For example: €1,200–€1,500 per month or Competitive.',max_length=160)),
        migrations.AddField(model_name='career',name='minimum_experience',field=models.CharField(blank=True,help_text='For example: 2 years or Entry level.',max_length=120)),
        migrations.AddField(model_name='career',name='minimum_commitment_years',field=models.PositiveSmallIntegerField(blank=True,help_text='Minimum expected commitment in years.',null=True)),
        migrations.AddField(model_name='career',name='job_description',field=models.TextField(blank=True,help_text='Explain the role, day-to-day work and who the person will work with.')),
        migrations.AddField(model_name='career',name='requirements',field=models.TextField(blank=True,help_text='List qualifications, skills and experience. Use one requirement per line.')),
        migrations.AddField(model_name='career',name='application_instructions',field=models.TextField(blank=True,help_text='Tell applicants what to submit and how to apply.')),
        migrations.AddField(model_name='career',name='status',field=models.CharField(choices=[('open','Open'),('closed','Closed')],default='open',help_text='Open vacancies accept applications. Closed vacancies remain visible but cannot be applied for.',max_length=10)),
        migrations.RunPython(convert_career_sections, migrations.RunPython.noop),
        migrations.DeleteModel(name='CareerSection'),
    ]
