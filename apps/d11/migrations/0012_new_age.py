from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0011_ru'),
    ]

    operations = [
        migrations.AddField(
            model_name='doc',
            name='is_checked',
            field=models.BooleanField(default=True, verbose_name='проверено'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_checked',
            field=models.BooleanField(default=False, verbose_name='проверено'),
        ),
        migrations.CreateModel(
            name='DocAdvancedAttributes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=500, null=True)),
                ('defense_date', models.DateField(blank=True, null=True)),
                ('values_created_at_max', models.DateTimeField(blank=True, null=True)),
                ('values_created_at_min', models.DateTimeField(blank=True, null=True)),
                ('values_updated_at_max', models.DateTimeField(blank=True, null=True)),
                ('values_updated_at_min', models.DateTimeField(blank=True, null=True)),
                ('aleph_card_synopsis_id', models.BigIntegerField(blank=True, null=True)),
                ('aleph_card_synopsis_aleph_id', models.CharField(blank=True, max_length=20, null=True)),
                ('aleph_card_synopsis_aleph_created_at', models.DateTimeField(blank=True, null=True)),
                ('aleph_card_synopsis_aleph_updated_at', models.DateTimeField(blank=True, null=True)),
                ('aleph_card_dissertation_id', models.BigIntegerField(blank=True, null=True)),
                ('aleph_card_dissertation_aleph_id', models.CharField(blank=True, max_length=20, null=True)),
                ('aleph_card_dissertation_created_at', models.DateTimeField(blank=True, null=True)),
                ('aleph_card_dissertation_updated_at', models.DateTimeField(blank=True, null=True)),
                ('doc',
                 models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='advanced_attributes',
                                   to='d11.doc')),
            ],
            options={
                'db_table': 'vm_d11_doc_advanced_attributes',
                'managed': False,
            },
        ),

        migrations.RenameField(
            model_name='doc',
            old_name='is_autoref_exist',
            new_name='is_synopsis_exists',
        ),
        migrations.RemoveField(
            model_name='doc',
            name='is_sync_abis',
        ),
        migrations.AddField(
            model_name='doc',
            name='is_sync_dissertation_to_abis',
            field=models.BooleanField(default=True, verbose_name='загрузить диссертацию в Алеф'),
        ),
        migrations.AddField(
            model_name='doc',
            name='is_sync_synopsis_to_abis',
            field=models.BooleanField(default=True, verbose_name='загрузить автореферат в Алеф'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_sync_dissertation_to_abis',
            field=models.BooleanField(default=False, verbose_name='загрузить диссертацию в Алеф'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_sync_synopsis_to_abis',
            field=models.BooleanField(default=False, verbose_name='загрузить автореферат в Алеф'),
        ),
        migrations.RemoveField(
            model_name='doc',
            name='is_ready_for_abis',
        ),
        migrations.AddField(
            model_name='doc',
            name='last_date_abis_manual_changes',
            field=models.DateTimeField(blank=True,
                                       help_text='Справочное поле, заполняется при экспорте автореферата или '
                                                 'диссертации в Алеф, а после этого вручную',
                                       null=True, verbose_name='дата последнего сделанного в Алеф изменения'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_sync_dissertation_to_abis',
            field=models.BooleanField(default=False, help_text='по достижению даты защиты',
                                      verbose_name='загрузить диссертацию в Алеф'),
        ),
        migrations.AlterField(
            model_name='doc',
            name='is_track_external',
            field=models.BooleanField(default=True, verbose_name='отслеживать ВАК'),
        ),
        migrations.CreateModel(
            name='DocFullNameDoubles',
            fields=[
                ('doc', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True,
                                             related_name='full_name_doubles', serialize=False, to='d11.doc')),
                ('full_name', models.CharField(max_length=500)),
                ('docs_count', models.IntegerField()),
                ('docs_ids', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), size=None)),
            ],
            options={
                'db_table': 'vm_d11_doc_full_name_doubles',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='exporttoaleph',
            name='kind',
            field=models.CharField(choices=[('create_full', 'Создание обеих карточек'),
                                            ('create_synopsis', 'Создание авторефератов'),
                                            ('create_dissertation', 'Создание диссертаций'),
                                            ('update_full', 'Обновление обеих карточек'),
                                            ('update_synopsis', 'Обновление авторефератов'),
                                            ('update_dissertation', 'Обновление диссертаций')], max_length=50,
                                   verbose_name='тип'),
        ),
        migrations.RemoveField(
            model_name='doc',
            name='is_synopsis_exists',
        ),

        migrations.AlterField(
            model_name='exporttoaleph',
            name='kind',
            field=models.CharField(
                choices=[('create_full', 'Создание обеих карточек'), ('create_synopsis', 'Создание авторефератов'),
                         ('create_dissertation', 'Создание диссертаций'), ('update_full', 'Обновление обеих карточек'),
                         ('update_synopsis', 'Обновление авторефератов'),
                         ('update_dissertation', 'Обновление диссертаций'),
                         ('link_set', 'Установка связей между карточками автореферата и диссертации')], max_length=50,
                verbose_name='тип'),
        ),
        migrations.AlterField(
            model_name='exporttoaleph',
            name='kind',
            field=models.CharField(
                choices=[('create_full', 'Создание обеих карточек'), ('create_synopsis', 'Создание авторефератов'),
                         ('create_dissertation', 'Создание диссертаций'), ('update_full', 'Обновление обеих карточек'),
                         ('update_synopsis', 'Обновление авторефератов'),
                         ('update_dissertation', 'Обновление диссертаций')], max_length=50, verbose_name='тип'),
        ),
        migrations.RunSQL('''
            UPDATE d11_exporttoaleph SET kind = 'create_full' WHERE kind = 'create_with_autoref';
            UPDATE d11_exporttoaleph SET kind = 'create_dissertation' WHERE kind = 'create_without_autoref';
            UPDATE d11_exporttoaleph SET kind = 'update_full' WHERE kind = 'update_with_autoref';
            UPDATE d11_exporttoaleph SET kind = 'update_dissertation' WHERE kind = 'update_without_autoref';
        ''', ''),
    ]
