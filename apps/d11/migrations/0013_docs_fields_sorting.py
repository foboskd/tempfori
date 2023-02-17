from django.core.management import call_command
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0012_new_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='docfield',
            name='sorting',
            field=models.IntegerField(default=0, verbose_name='сортировка'),
        ),
        migrations.AlterModelOptions(
            name='docfield',
            options={'ordering': ['sorting', 'name'], 'verbose_name': 'поле записей',
                     'verbose_name_plural': 'поля записей'},
        ),
        migrations.AlterModelOptions(
            name='docfieldvalue',
            options={'ordering': ['field__sorting'], 'verbose_name': 'значение поля записи',
                     'verbose_name_plural': 'значения полей записи'},
        ),
        migrations.AlterModelOptions(
            name='docfield',
            options={'ordering': ['sorting', 'name', 'label'], 'verbose_name': 'поле записей',
                     'verbose_name_plural': 'поля записей'},
        ),
        migrations.AlterModelOptions(
            name='docfieldvalue',
            options={'ordering': ['field__sorting', 'field__name', 'field__label'],
                     'verbose_name': 'значение поля записи', 'verbose_name_plural': 'значения полей записи'},
        ),
        migrations.RunPython(lambda *x: call_command('setup_celery_schedule', force=True), lambda *x: None),
        migrations.RunPython(lambda *x: call_command('setup_doc_fields', force=True), lambda *x: None),
    ]
