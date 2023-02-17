from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0008_source_is_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='doc',
            name='is_autoref_exist',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='doc',
            name='is_ready_for_abis',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_ready_for_abis',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_autoref_exist',
            field=models.BooleanField(default=False),
        ),
    ]
