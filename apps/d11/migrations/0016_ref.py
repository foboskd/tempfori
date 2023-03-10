# Generated by Django 3.2.12 on 2022-04-29 12:36

import d11.models.doc
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('d11', '0015_docs_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='docfilevalue',
            name='value',
            field=models.FileField(help_text='актуально только для в случае, если не создана соответствующая карточка Алеф', upload_to=d11.models.doc.doc_file_value_upload_to, verbose_name='файл'),
        ),
        migrations.CreateModel(
            name='Ref',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('kind', 'Тип диссертации'), ('industry', 'Отрасль науки')], max_length=20)),
                ('from_what', models.CharField(max_length=500)),
                ('to_what', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'замена для Алефа',
                'verbose_name_plural': 'замены для Алефа',
                'ordering': ['type', 'from_what'],
                'unique_together': {('type', 'from_what')},
            },
        ),
    ]
