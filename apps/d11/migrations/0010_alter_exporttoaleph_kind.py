from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0009_ready_and_autoref_bools'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttoaleph',
            name='kind',
            field=models.CharField(choices=[('create_with_autoref', 'Create With Autoref'),
                                            ('create_without_autoref', 'Create Without Autoref'),
                                            ('update_with_autoref', 'Update With Autoref'),
                                            ('update_without_autoref', 'Update Without Autoref')], max_length=50),
        ),
        migrations.RunSQL('''
UPDATE d11_exporttoaleph SET kind = 'create_with_autoref' WHERE kind = 'create';
UPDATE d11_exporttoaleph SET kind = 'update_with_autoref' WHERE kind = 'update';
        ''')
    ]
