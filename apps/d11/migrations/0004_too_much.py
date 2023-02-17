import django.db.models.deletion
from django.db import migrations, models
import project.contrib.db.upload_to
import d11.models.doc
import d11.models.aleph


class Migration(migrations.Migration):
    dependencies = [
        ('d11', '0003_aleph_ids'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='doc',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='docfieldvalue',
            options={'ordering': ['-id']},
        ),
        migrations.RemoveField(
            model_name='doc',
            name='aleph_dissertation_id',
        ),
        migrations.RemoveField(
            model_name='doc',
            name='aleph_dissertation_id_date',
        ),
        migrations.RemoveField(
            model_name='doc',
            name='aleph_synopsis_id',
        ),
        migrations.RemoveField(
            model_name='doc',
            name='aleph_synopsis_id_date',
        ),
        migrations.CreateModel(
            name='DocAlephCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind',
                 models.CharField(choices=[('synopsis', 'Synopsis'), ('dissertation', 'Dissertation')], max_length=50)),
                ('aleph_id', models.CharField(blank=True, max_length=100, null=True)),
                ('aleph_fields_json', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aleph_cards',
                                          to='d11.doc')),
            ],
            options={
                'unique_together': {('doc', 'kind')},
            },
        ),
        migrations.AlterField(
            model_name='docfield',
            name='type',
            field=models.CharField(
                choices=[('str', 'Строка'), ('int', 'Целое число'), ('float', 'Число'), ('date', 'Дата'),
                         ('datetime', 'Дата и время'), ('file', 'Файл')], default='str', max_length=50),
        ),
        migrations.CreateModel(
            name='ImportFromAleph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('docs_serialized_file', models.FileField(upload_to=project.contrib.db.upload_to.upload_to)),
                ('kind', models.CharField(choices=[('create', 'New'), ('update', 'Update')], max_length=20)),
                ('extra', models.JSONField(default=dict)),
                ('docs', models.ManyToManyField(related_name='importfromaleph', to='d11.Doc')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExportToAleph',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('docs_serialized_file', models.FileField(upload_to=project.contrib.db.upload_to.upload_to)),
                ('kind', models.CharField(choices=[('create', 'New'), ('update', 'Update')], max_length=20)),
                ('extra', models.JSONField(default=dict)),
                ('docs', models.ManyToManyField(related_name='exporttoaleph', to='d11.Doc')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),

        migrations.AlterField(
            model_name='exporttoaleph',
            name='kind',
            field=models.CharField(choices=[('create', 'Create'), ('update', 'Update')], max_length=20),
        ),
        migrations.AlterField(
            model_name='importfromaleph',
            name='kind',
            field=models.CharField(choices=[('create', 'Create'), ('update', 'Update')], max_length=20),
        ),
        migrations.AlterField(
            model_name='exporttoaleph',
            name='docs',
            field=models.ManyToManyField(related_name='_d11_exporttoaleph_docs_+', to='d11.Doc'),
        ),
        migrations.AlterField(
            model_name='importfromaleph',
            name='docs',
            field=models.ManyToManyField(related_name='_d11_importfromaleph_docs_+', to='d11.Doc'),
        ),
        migrations.CreateModel(
            name='CollectorImport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('extra', models.JSONField(default=dict)),
                ('docs', models.ManyToManyField(related_name='_d11_collectorimport_docs_+', to='d11.Doc')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='collectorimport',
            name='collector_name',
            field=models.CharField(default='', max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exporttoaleph',
            name='result_file',
            field=models.FileField(blank=True, null=True,
                                   upload_to=d11.models.aleph.import_export_upload_to_result_file),
        ),
        migrations.AddField(
            model_name='importfromaleph',
            name='result_file',
            field=models.FileField(blank=True, null=True,
                                   upload_to=d11.models.aleph.import_export_upload_to_result_file),
        ),
        migrations.AlterField(
            model_name='exporttoaleph',
            name='docs_serialized_file',
            field=models.FileField(blank=True, null=True,
                                   upload_to=d11.models.aleph.import_export_upload_to_serialized_file),
        ),
        migrations.AlterField(
            model_name='importfromaleph',
            name='docs_serialized_file',
            field=models.FileField(blank=True, null=True,
                                   upload_to=d11.models.aleph.import_export_upload_to_serialized_file),
        ),
        migrations.AlterField(
            model_name='docalephcard',
            name='aleph_fields_json',
            field=models.JSONField(default=dict),
        ),
        migrations.RemoveField(
            model_name='importfromaleph',
            name='kind',
        ),

        migrations.AddField(
            model_name='doc',
            name='content_file',
            field=models.FileField(blank=True, null=True, upload_to=d11.models.doc.doc_upload_to),
        ),

        migrations.AddField(
            model_name='doc',
            name='content_file_hash',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),

        migrations.AddField(
            model_name='doc',
            name='is_track_abis',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='doc',
            name='is_track_external',
            field=models.BooleanField(default=True),
        ),
        migrations.RenameField(
            model_name='doc',
            old_name='is_track_abis',
            new_name='is_sync_abis',
        ),
        migrations.AddField(
            model_name='docalephcard',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=d11.models.doc_aleph.doc_aleph_card_upload_to),
        ),
    ]
