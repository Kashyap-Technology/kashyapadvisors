from django.db import migrations, models
import django.utils.timezone


def seed_official_updates(apps, schema_editor):
    Update = apps.get_model('platform_app', 'OfficialUpdate')
    Update.objects.get_or_create(
        slug='italy-scholarships-accommodation-official-guide',
        defaults=dict(
            title='Scholarships and accommodation: start with the official regional guidance',
            summary='Universitaly explains regional right-to-study support, university benefits and accommodation. Requirements and calls vary by region and institution.',
            body='Italy offers support through regional right-to-study bodies, university scholarships and other public or private schemes. International students may need an ISEE parificato or equivalent financial documentation, depending on the current call. Accommodation and benefits are published through the relevant region or university, so always check the current call, eligibility rules, documents and deadline before applying.\n\nUse the official Universitaly pages to identify the regional body, university benefits and accommodation options connected to your destination.',
            kind='scholarship', source_label='Universitaly · Scholarships and benefits', source_url='https://www.universitaly.it/en/borse-studio',
            published_at=django.utils.timezone.now(), published=True, pinned=True,
        ),
    )
    Update.objects.get_or_create(
        slug='imat-2026-registration-window-closed',
        defaults=dict(
            title='IMAT 2026: registration window closed',
            summary='For the 2026/27 English-taught medicine admission test, registration ran from 26 August to 9 September 2026 at 15:00 Italian time. The test is scheduled for 29 September 2026.',
            body='The official 2026/27 IMAT registration window has ended. The Ministry of University and Research lists the English-taught Medicine, Dentistry and Veterinary Medicine selection date as 30 September 2026 in its July notice, while the later official university guidance for IMAT registration and test scheduling states 29 September 2026. Students should follow the final ministerial call and the Universitaly registration record for their exact procedure.\n\nDo not pay an agent or rely on an old deadline. For the next cycle, check the Ministry, Universitaly and the target university’s official admission call before planning registration.',
            kind='deadline', source_label='MUR and official university IMAT guidance', source_url='https://www.mur.gov.it/it/news/martedi-07072026/universita-fissate-le-date-delle-prove-dammissione-le-facolta-ad-accesso',
            published_at=django.utils.timezone.now(), published=True, pinned=False,
        ),
    )


class Migration(migrations.Migration):
    dependencies=[('platform_app','0011_social_links')]
    operations=[
        migrations.CreateModel(
            name='OfficialUpdate',
            fields=[
                ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
                ('title',models.CharField(max_length=240)),
                ('slug',models.SlugField(max_length=240,unique=True)),
                ('summary',models.TextField(help_text='Short text shown in the alert and update list.')),
                ('body',models.TextField(help_text='Detailed explanation. Use a blank line between paragraphs.')),
                ('kind',models.CharField(choices=[('deadline','Deadline / test'),('scholarship','Scholarship / accommodation'),('admission','Admission update'),('general','General update')],default='general',max_length=30)),
                ('source_label',models.CharField(default='Official source',max_length=160)),
                ('source_url',models.URLField()),
                ('published_at',models.DateTimeField()),
                ('expires_at',models.DateTimeField(blank=True,help_text='Optional. Hide this update from the live alert after this time.',null=True)),
                ('published',models.BooleanField(default=False)),
                ('pinned',models.BooleanField(default=False,help_text='Show this update as the live notice on the homepage.')),
            ],
            options={'ordering':['-pinned','-published_at','-pk'],'verbose_name':'Official update','verbose_name_plural':'Official updates'},
        ),
        migrations.RunPython(seed_official_updates,migrations.RunPython.noop),
    ]
