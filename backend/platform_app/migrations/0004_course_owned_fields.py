from django.db import migrations, models
import django.db.models.deletion


def copy_definitions(apps,schema_editor):
    Value=apps.get_model('platform_app','CourseFieldValue')
    used={}
    for value in Value.objects.select_related('field').order_by('pk'):
        definition=value.field
        labels=used.setdefault(value.course_id,set())
        label=definition.label
        suffix=1
        while label in labels:
            suffix+=1
            label=f'{definition.label[:150]} ({suffix})'
        labels.add(label)
        value.label=label
        value.key=definition.key
        value.presentation=definition.presentation
        value.order=definition.order
        value.active=definition.active
        value.save(update_fields=['label','key','presentation','order','active'])


class Migration(migrations.Migration):
    dependencies=[('platform_app','0003_default_course_fields')]
    operations=[
        migrations.RemoveConstraint(model_name='coursefieldvalue',name='unique_course_field_value'),
        migrations.AddField(model_name='coursefieldvalue',name='label',field=models.CharField(max_length=160,default=''),preserve_default=False),
        migrations.AddField(model_name='coursefieldvalue',name='key',field=models.SlugField(blank=True,editable=False)),
        migrations.AddField(model_name='coursefieldvalue',name='presentation',field=models.CharField(max_length=10,choices=[('fact','Overview row'),('section','Detailed section')],default='fact')),
        migrations.AddField(model_name='coursefieldvalue',name='order',field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name='coursefieldvalue',name='active',field=models.BooleanField(default=True,help_text='Show this field on this course’s public page.')),
        migrations.RunPython(copy_definitions,migrations.RunPython.noop),
        migrations.AlterField(model_name='coursefieldvalue',name='field',field=models.ForeignKey(to='platform_app.coursefield',on_delete=django.db.models.deletion.SET_NULL,related_name='values',null=True,blank=True,editable=False)),
        migrations.AlterModelOptions(name='coursefieldvalue',options={'ordering':['order','pk'],'verbose_name':'Course field','verbose_name_plural':'Course fields'}),
        migrations.AddConstraint(model_name='coursefieldvalue',constraint=models.UniqueConstraint(fields=['course','label'],name='unique_course_field_label')),
    ]
