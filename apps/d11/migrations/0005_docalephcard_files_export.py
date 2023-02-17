# Generated by Django 3.2.8 on 2021-11-05 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('d11', '0004_too_much'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocAlephCardFilesExport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_all', models.BooleanField(default=False)),
                ('extra', models.JSONField(default=dict)),
                ('cards', models.ManyToManyField(related_name='files_exports', to='d11.DocAlephCard')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
