# Generated by Django 3.2.12 on 2022-02-09 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailnotification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='создано'),
        ),
        migrations.AlterField(
            model_name='emailnotification',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='обновлено'),
        ),
    ]