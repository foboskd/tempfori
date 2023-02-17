# Generated by Django 3.2.4 on 2021-06-27 23:25

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=1000, unique=True)),
                ('label_aliases', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1000), blank=True, null=True, size=None)),
                ('type', models.CharField(choices=[('str', 'Str'), ('int', 'Int'), ('float', 'Float'), ('date', 'Date'), ('datetime', 'Datetime')], default='str', max_length=50)),
                ('is_auto', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=1000, unique=True)),
                ('collector_class', models.CharField(choices=[['CollectorVakAdvert', 'ВАК :: ОБЪЯВЛЕНИЯ О ЗАЩИТАХ ВАК'], ['CollectorVakIndependent', 'ВАК :: САМОСТОЯТЕЛЬНОЕ ПРИСУЖДЕНИЕ СТЕПЕНЕЙ']], max_length=100)),
                ('attributes', models.JSONField(blank=True, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Doc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=1000, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='d11.source')),
            ],
        ),
        migrations.CreateModel(
            name='DocFieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields_values', to='d11.doc')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docs_values', to='d11.docfield')),
            ],
            options={
                'index_together': {('doc', 'field')},
            },
        ),
    ]