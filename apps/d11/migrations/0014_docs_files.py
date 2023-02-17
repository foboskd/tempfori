import d11.models.doc
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0013_docs_fields_sorting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docfieldvalue',
            name='field',
            field=models.ForeignKey(limit_choices_to=models.Q(('type', 'file'), _negated=True),
                                    on_delete=django.db.models.deletion.CASCADE, related_name='docs_values',
                                    to='d11.docfield', verbose_name='поле'),
        ),
        migrations.CreateModel(
            name='DocFileValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='обновлено')),
                ('value', models.FileField(upload_to=d11.models.doc.doc_file_value_upload_to, verbose_name='файл')),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files_values',
                                          to='d11.doc', verbose_name='запись')),
                ('field', models.ForeignKey(limit_choices_to=models.Q(('type', 'file')),
                                            on_delete=django.db.models.deletion.CASCADE, related_name='docs_files',
                                            to='d11.docfield', verbose_name='поле')),
            ],
            options={
                'verbose_name': 'файл записи',
                'verbose_name_plural': 'файлы записи',
                'ordering': ['field__sorting', 'field__name', 'field__label'],
                'unique_together': {('doc', 'field')},
            },
        ),
    ]
